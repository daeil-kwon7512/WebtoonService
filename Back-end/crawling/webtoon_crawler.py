import sqlite3 
import pandas as pd
import numpy as np
import pymysql
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
import time
import requests
import re
from tqdm import tqdm
import json
from collections import defaultdict
import concurrent.futures

def Naver_webtoon_crawler():
    day = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}

    webtoon_list = []
    writers_list = []
    painters_list = []
    novel_origin_authors_list = []

    for day_code in tqdm(day):
        url = f'https://comic.naver.com/api/webtoon/titlelist/weekday?week={day_code}&order=user'
        
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            
            # 웹툰 하나씩 꺼내기 (변수명 i -> webtoon 으로 변경)
            for webtoon in data["titleList"]:
                
                # 공통 ID (Foreign Key 역할)
                t_id = int(webtoon["titleId"])
                
                # 웹으로 바로 이동할 수 있는 url
                site_url = f'https://comic.naver.com/webtoon/list?titleId={t_id}&tab={day_code}'
                
                # 1. 메인 웹툰 정보 (불필요한 작가 문자열 제거)
                webtoon_list.append({
                    "titleId": t_id,
                    "titleName": webtoon["titleName"],
                    "url": site_url,
                    "thumbnailUrl": webtoon["thumbnailUrl"],
                    "up": webtoon["up"],
                    "rest": webtoon["rest"],
                    "bm": webtoon["bm"],
                    "adult": webtoon["adult"],
                    "starScore": float(webtoon["starScore"]),
                    "viewCount": int(webtoon["viewCount"]),
                    "openToday": webtoon["openToday"],
                    "potenUp": webtoon["potenUp"],
                    "bestChallengeLevelUp": webtoon["bestChallengeLevelUp"],
                    "finish": webtoon["finish"],
                    "new": webtoon["new"]
                })
                
                # 2. 글 작가 (titleId 추가 필수!)
                if webtoon.get("writers"):
                    for writer in webtoon["writers"]:
                        writers_list.append({
                            "titleId": t_id,      # <--- 이게 있어야 연결됩니다!
                            "writerId": int(writer["id"]),
                            "name": writer["name"],
                            "type": "Writer"      # 구분용 (선택사항)
                        })
                
                # 3. 그림 작가 (titleId 추가 필수!)
                if webtoon.get("painters"):
                    for painter in webtoon["painters"]:
                        painters_list.append({
                            "titleId": t_id,      # <--- 이게 있어야 연결됩니다!
                            "painterId": int(painter["id"]),
                            "name": painter["name"],
                            "type": "Painter"     # 구분용 (선택사항)
                        })
                        
                # 4. 원작 작가 (titleId 추가 필수!)
                if webtoon.get("novelOriginAuthors"):
                    for origin_author in webtoon["novelOriginAuthors"]:
                        novel_origin_authors_list.append({
                            "titleId": t_id,      # <--- 이게 있어야 연결됩니다!
                            "originAuthorId": int(origin_author["id"]),
                            "name": origin_author["name"],
                            "type": "Original"    # 구분용 (선택사항)
                        })
            time.sleep(1)

        else:
            print("에러:", response.status_code)

    webtoon_df = pd.DataFrame(webtoon_list).drop_duplicates()
    writers_df = pd.DataFrame(writers_list).drop_duplicates()
    painters_df = pd.DataFrame(painters_list).drop_duplicates()
    novelOriginAuthors_df = pd.DataFrame(novel_origin_authors_list).drop_duplicates()
    
    webtoon_df = webtoon_df.drop(["rest", "bm", "starScore", "viewCount", "openToday", "potenUp", "bestChallengeLevelUp", "new"], axis=1)
    
    wirters_pivot = (
        writers_df
        .groupby(["titleId", "type"])["name"]
        .agg(lambda s: ", ".join(sorted(set(s))))
        .unstack(fill_value="")         # role을 컬럼으로 피벗
        .reset_index()
    )

    webtoon_df = webtoon_df.merge(wirters_pivot, on="titleId", how="left")
    
    painters_pivot = (
        painters_df
        .groupby(["titleId", "type"])["name"]
        .agg(lambda s: ", ".join(sorted(set(s))))
        .unstack(fill_value="")         # role을 컬럼으로 피벗
        .reset_index()
    )

    webtoon_df = webtoon_df.merge(painters_pivot, on="titleId", how="left")
    
    original_pivot = (
        novelOriginAuthors_df
        .groupby(["titleId", "type"])["name"]
        .agg(lambda s: ", ".join(sorted(set(s))))
        .unstack(fill_value="")         # role을 컬럼으로 피벗
        .reset_index()
    )

    webtoon_df = webtoon_df.merge(original_pivot, on="titleId", how="left")
    
    # 1. 데이터를 담을 5개의 그릇 준비 (DB 테이블 구조와 1:1 매칭)
    detail_list = []        # 줄거리 등 기본 정보 (1:1)
    genre_list = []         # 장르 (1:N)
    keyword_tag_list = []   # 단순 텍스트 태그 (1:N) - gfpAdCustomParam 안의 tags
    weekday_list = []       # 요일 (1:N)
    curation_tag_list = []  # 큐레이션 태그 상세 정보 (1:N)

    # 2. 중복된 ID 제거 (API 호출 횟수 줄이기)
    unique_ids = webtoon_df['titleId'].unique()

    # 3. 세션 사용 (속도 향상 팁: 매번 연결을 새로 맺지 않고 재사용)
    session = requests.Session()
    session.headers.update(headers)

    for page_num in tqdm(unique_ids):
        url = f'https://comic.naver.com/api/article/list/info?titleId={page_num}'
        
        try:
            response = session.get(url) # requests.get 대신 session.get 사용
            
            if response.status_code == 200:
                data = response.json()
                t_id = int(data["titleId"])
                
                # ---------------------------------------------------
                # [1] 메인 상세 정보 (Synopsis)
                # ---------------------------------------------------
                detail_list.append({
                    "titleId": t_id,
                    "synopsis": data.get("synopsis", ""), # 없을 경우 대비
                    # 필요한 다른 정보가 있다면 여기 추가
                })
                
                # gfpAdCustomParam 데이터 가져오기 (없을 수도 있으니 get 사용)
                gfp_data = data.get("gfpAdCustomParam", {})
                
                # ---------------------------------------------------
                # [2] 장르 (Genre) - 리스트 풀어서 저장
                # ---------------------------------------------------
                # 예: ['DRAMA', 'ROMANCE'] -> 각각 저장
                if gfp_data.get("genreTypes"):
                    for genre in gfp_data["genreTypes"]:
                        genre_list.append({
                            "titleId": t_id,
                            "genre": genre
                        })
                        
                # ---------------------------------------------------
                # [3] 텍스트 태그 (Tags) - 리스트 풀어서 저장
                # ---------------------------------------------------
                # 예: ['사이다', '먼치킨'] -> 각각 저장
                if gfp_data.get("tags"):
                    for tag in gfp_data["tags"]:
                        keyword_tag_list.append({
                            "titleId": t_id,
                            "tag": tag
                        })

                # ---------------------------------------------------
                # [4] 요일 (Weekdays) - 리스트 풀어서 저장
                # ---------------------------------------------------
                if gfp_data.get("weekdays"):
                    for day in gfp_data["weekdays"]:
                        weekday_list.append({
                            "titleId": t_id,
                            "day": day
                        })

                # ---------------------------------------------------
                # [5] 큐레이션 태그 (Curation Tags) - titleId 필수 추가!
                # ---------------------------------------------------
                if data.get("curationTagList"):
                    for tag_obj in data["curationTagList"]:
                        curation_tag_list.append({
                            "titleId": t_id,         # <--- 핵심: 연결고리 추가
                            "tagId": tag_obj.get("id"),
                            "tagName": tag_obj.get("tagName"),
                            "urlPath": tag_obj.get("urlPath"),
                            "curationType": tag_obj.get("curationType")
                        })
                        
            else:
                print(f"ID {page_num} 에러: {response.status_code}")
            
            time.sleep(1)
                
        except Exception as e:
            print(f"ID {page_num} 접속 중 예외 발생: {e}")

    # --- 결과 확인 (판다스 변환) ---
    df_detail = pd.DataFrame(detail_list)
    df_genre = pd.DataFrame(genre_list)
    df_keyword = pd.DataFrame(keyword_tag_list)
    df_weekday = pd.DataFrame(weekday_list)
    df_curation = pd.DataFrame(curation_tag_list)
    
    webtoon_df = webtoon_df.merge(df_detail, on="titleId", how="left")
    
    kw_agg = (
        df_keyword
        .groupby("titleId")["tag"]
        .agg(lambda s: ", ".join(sorted(set(s))))
        .reset_index()
    )

    # 2) 장르 df와 merge
    df_genre_kw = df_genre.merge(kw_agg, on="titleId", how="left")  # genre, tag 두 컬럼

    # 3) genre 컬럼에 장르 + 키워드 합치기
    def merge_genre_keywords(row):
        g = str(row["genre"]).strip()          # DRAMA, ACTION ...
        t = str(row["tag"]).strip()
        if not t or t == "nan":
            return g
        return f"{g}, {t}"

    df_genre_kw["genre"] = df_genre_kw.apply(merge_genre_keywords, axis=1)

    # 키워드 컬럼이 더 필요 없으면
    df_genre_kw = df_genre_kw.drop(columns=["tag"])
    webtoon_df = webtoon_df.merge(df_genre_kw, on="titleId", how="left")
    
    wk_agg = (
        df_weekday
        .groupby("titleId")["day"]
        .agg(lambda s: ", ".join(sorted(set(s))))
        .reset_index()
    )

    base_agg = (
        webtoon_df
        .sort_values("titleId")           # 필요하면 기준 정렬
        .groupby("titleId", as_index=False)
        .first()                          # 같은 titleId 행이 여러 개면 첫 번째만 사용
    )

    naver_webtoons = webtoon_df.merge(wk_agg, on="titleId", how="left") 
    naver_webtoons = naver_webtoons.drop(["finish"], axis=1)
    naver = naver_webtoons.rename(columns={
        "url": "Url",
        "adult": "is_adult",
        "up": 'is_up',
    })

    naver = naver[["titleId","titleName","Url","thumbnailUrl","is_adult",
                    "Writer","Painter","Original","synopsis","genre","day","is_up"]]
    naver["provider"] = "NAVER"
    
    return naver

def Kakao_webtoon_crawler():
    day = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'}

    webtoon_list = []
    writers_list = []
    painters_list = []
    novel_origin_authors_list = []

    for day_code in tqdm(day):
        url = f'https://gateway-kw.kakao.com/section/v2/timetables/days?placement=timetable_{day_code}'

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            # pprint(data)
            for block in data.get("data", []):
                weekday = block.get("title")
                for group in block.get("cardGroups", []):
                    for card in group.get("cards", []):
                        content = card.get("content", {})
                        additional = card.get("additional", {})
                        authors = content.get("authors", [])
                        badges = content.get("badges", [])
                        genre_filters = card.get("genreFilters", [])
                        adult_filters = card.get("additional", {})

                        author_names = ", ".join(a.get("name", "") for a in authors)
                        badge_titles = [b.get("title", "") for b in badges]

                        row = {
                            "웹툰ID": content.get("id"),
                            "제목": content.get("title"),
                            "seoId": content.get("seoId"),
                            "url": f'https://webtoon.kakao.com/content/{content.get("seoId")}/{content.get("id")}',
                            "thumbnailurl" : content.get("featuredCharacterImageA")+'.png',
                            "장르필터": ", ".join(genre_filters),
                            "카피문구": content.get("catchphraseTwoLines"),
                            "작가들": author_names,
                            "뱃지목록": ", ".join(badge_titles),
                            "UP여부": any(t == "up" for t in badge_titles),
                            "성인여부": adult_filters.get("adult"),
                            "요일": weekday,
                        }
                        webtoon_list.append(row)
            time.sleep(1)

        else:
            print("에러:", response.status_code)
            
    df = pd.DataFrame(webtoon_list)

    cols_keep = ["웹툰ID", "제목", "seoId", "url", "thumbnailurl", "장르필터",
                "카피문구", "작가들", "뱃지목록", "UP여부", "성인여부"]

    df = (
        df.groupby(cols_keep, as_index=False)["요일"]
        .agg(lambda s: ", ".join(sorted(set(s))))
    )
    
    API_URL = "https://gateway-kw.kakao.com/decorator/v2/decorator/contents/{id}/profile"
    
    def fetch_detail(content_id: int) -> dict:
        url = API_URL.format(id=content_id)
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()["data"]
    
    def parse_detail(detail: dict) -> dict:
        synopsis = detail.get("synopsis", "")

        raw_keywords = detail.get("seoKeywords", []) or []
        seo_keywords = [kw.lstrip("#").strip() for kw in raw_keywords]

        authors = detail.get("authors", []) or []
        writers, artists, originals = [], [], []

        for a in authors:
            name = (a.get("name") or "").strip()
            role = a.get("type")
            if not name:
                continue

            if role == "AUTHOR":
                writers.append(name)
            elif role == "ILLUSTRATOR":
                artists.append(name)
            elif role == "ORIGINAL_STORY":
                originals.append(name)

        return {
            "synopsis": synopsis,
            "seo_keywords": seo_keywords,
            "writers": writers,
            "artists": artists,
            "original_authors": originals,
        }

    rows = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        webtoon_id = int(row["웹툰ID"])

        try:
            detail = fetch_detail(webtoon_id)
            parsed = parse_detail(detail)
        except Exception as e:
            print("failed:", webtoon_id, e)
            parsed = {
                "synopsis": "",
                "seo_keywords": [],
                "writers": [],
                "artists": [],
                "original_authors": [],
            }

        new_row = row.copy()
        new_row["시놉시스"] = parsed["synopsis"]
        new_row["키워드리스트"] = ", ".join(parsed["seo_keywords"])
        new_row["글작가"] = ", ".join(parsed["writers"])
        new_row["그림작가"] = ", ".join(parsed["artists"])
        new_row["원작가"] = ", ".join(parsed["original_authors"])
        rows.append(new_row)

    df_enriched = pd.DataFrame(rows)
    df_kakao = df_enriched.drop(["seoId", "뱃지목록", "작가들"], axis=1)
    
    def merge_genre_into_keywords(row):
        # 1) 장르필터에서 all 제거
        raw = str(row["장르필터"])
        genres = [g.strip() for g in raw.split(",") if g.strip() and g.strip().lower() != "all"]

        # 2) 기존 키워드리스트 분해
        kw_raw = str(row["키워드리스트"])
        if kw_raw in ("nan", "None"):
            keywords = []
        else:
            keywords = [k.strip() for k in kw_raw.split(",") if k.strip()]

        # 3) 두 리스트 합치고 중복 제거
        merged = []
        for x in keywords + genres:
            if x not in merged:
                merged.append(x)

        return ", ".join(merged)

    df_kakao["키워드리스트"] = df_kakao.apply(merge_genre_into_keywords, axis=1)
    df_kakao["장르필터"] = df_kakao["장르필터"].str.replace(r"\ball\b,?\s*", "", regex=True).str.strip(", ")
    
    df_kakao_final = df_kakao.drop(["장르필터"], axis=1)
    
    kakao = df_kakao_final.rename(columns={
        "웹툰ID": "titleId",
        "제목": "titleName",
        "thumbnailurl": "thumbnailUrl",
        "url": "Url",
        "성인여부": "is_adult",
        "시놉시스": "synopsis",
        "글작가": "Writer",
        "그림작가": "Painter",
        "원작가": "Original",
        "키워드리스트": "genre",   # or 별도 만든 장르+키워드 컬럼
        "요일": "day",
        "UP여부": 'is_up'
    })[["titleId","titleName","Url","thumbnailUrl","is_adult",
        "Writer","Painter","Original","synopsis","genre","day",'is_up']]
    
    kakao["provider"] = "KAKAO"
    
    return kakao

def Kpage_webtoon_crawler():
    # --- 공통 설정 ---
    REQUEST_URL = 'https://bff-page.kakao.com/graphql'
    HEADERS = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://page.kakao.com/', 
    }

    # --- 저장소 ---
    main_webtoon_list = []      
    all_series_ids = set()      

    # 요일 코드
    DAY_CODES = range(1, 8) 
    DAY_NAMES = {1: '월', 2: '화', 3: '수', 4: '목', 5: '금', 6: '토', 7: '일'}

    # ⚠️ 중요: 아까 찾아주신 '원본 쿼리' 전체입니다. 절대 줄이지 마세요!
    FULL_QUERY_STRING = """
    query staticLandingDayOfWeekLayout($queryInput: StaticLandingDayOfWeekParamInput!) {
    staticLandingDayOfWeekLayout(input: $queryInput) {
        ...Layout
    }
    }

    fragment Layout on Layout {
    id
    type
    sections {
        ...Section
    }
    screenUid
    }

    fragment Section on Section {
    id
    uid
    type
    title
    ... on RecommendSection {
        isRecommendArea
        isRecommendedItems
    }
    ... on DependOnLoggedInSection {
        loggedInTitle
        loggedInScheme
    }
    ... on SchemeSection {
        scheme
    }
    ... on MetaInfoTypeSection {
        metaInfoType
    }
    ... on TabSection {
        sectionMainTabList {
        uid
        title
        isSelected
        scheme
        additionalString
        subTabList {
            uid
            title
            isSelected
            groupId
        }
        }
    }
    ... on ThemeKeywordSection {
        themeKeywordList {
        uid
        title
        scheme
        }
    }
    ... on StaticLandingDayOfWeekSection {
        isEnd
        totalCount
        param {
        categoryUid
        businessModel {
            name
            param
        }
        subcategory {
            name
            param
        }
        dayTab {
            name
            param
        }
        page
        size
        screenUid
        }
        businessModelList {
        name
        param
        }
        subcategoryList {
        name
        param
        }
        dayTabList {
        name
        param
        }
        promotionBanner {
        ...PromotionBannerItem
        }
    }
    ... on StaticLandingTodayNewSection {
        totalCount
        param {
        categoryUid
        subcategory {
            name
            param
        }
        screenUid
        }
        categoryTabList {
        name
        param
        }
        subcategoryList {
        name
        param
        }
        promotionBanner {
        ...PromotionBannerItem
        }
        viewType
    }
    ... on StaticLandingTodayUpSection {
        isEnd
        totalCount
        param {
        categoryUid
        subcategory {
            name
            param
        }
        page
        }
        categoryTabList {
        name
        param
        }
        subcategoryList {
        name
        param
        }
    }
    ... on StaticLandingRankingSection {
        isEnd
        rankingTime
        totalCount
        param {
        categoryUid
        subcategory {
            name
            param
        }
        rankingType {
            name
            param
        }
        page
        screenUid
        }
        categoryTabList {
        name
        param
        }
        subcategoryList {
        name
        param
        }
        rankingTypeList {
        name
        param
        }
        displayAd {
        ...DisplayAd
        }
        promotionBanner {
        ...PromotionBannerItem
        }
        withOperationArea
        viewType
    }
    ... on StaticLandingGenreSection {
        isEnd
        totalCount
        param {
        categoryUid
        subcategory {
            name
            param
        }
        sortType {
            name
            param
        }
        page
        isComplete
        screenUid
        }
        subcategoryList {
        name
        param
        }
        sortTypeList {
        name
        param
        }
        displayAd {
        ...DisplayAd
        }
        promotionBanner {
        ...PromotionBannerItem
        }
    }
    ... on StaticLandingFreeSeriesSection {
        isEnd
        totalCount
        param {
        categoryUid
        tab {
            name
            param
        }
        page
        screenUid
        }
        tabList {
        name
        param
        }
        promotionBanner {
        ...PromotionBannerItem
        }
    }
    ... on StaticLandingEventSection {
        isEnd
        totalCount
        param {
        categoryUid
        page
        }
        categoryTabList {
        name
        param
        }
    }
    ... on StaticLandingOriginalSection {
        isEnd
        totalCount
        originalCount
        param {
        categoryUid
        subcategory {
            name
            param
        }
        sortType {
            name
            param
        }
        isComplete
        page
        screenUid
        }
        subcategoryList {
        name
        param
        }
        sortTypeList {
        name
        param
        }
        recommendItemList {
        ...Item
        }
    }
    ... on HelixThemeSection {
        subtitle
        isRecommendArea
    }
    groups {
        ...Group
    }
    }

    fragment PromotionBannerItem on PromotionBannerItem {
    title
    scheme
    leftImage
    rightImage
    eventLog {
        ...EventLogFragment
    }
    }

    fragment EventLogFragment on EventLog {
    fromGraphql
    click {
        layer1
        layer2
        setnum
        ordnum
        copy
        imp_id
        imp_provider
    }
    eventMeta {
        id
        name
        subcategory
        category
        series
        provider
        series_id
        type
    }
    viewimp_contents {
        type
        name
        id
        imp_area_ordnum
        imp_id
        imp_provider
        imp_type
        layer1
        layer2
    }
    customProps {
        landing_path
        view_type
        helix_id
        helix_yn
        helix_seed
        content_cnt
        event_series_id
        event_ticket_type
        play_url
        banner_uid
    }
    }

    fragment DisplayAd on DisplayAd {
    sectionUid
    bannerUid
    treviUid
    momentUid
    }

    fragment Item on Item {
    id
    type
    ...BannerItem
    ...OnAirItem
    ...CardViewItem
    ...CleanViewItem
    ... on DisplayAdItem {
        displayAd {
        ...DisplayAd
        }
    }
    ...PosterViewItem
    ...StrategyViewItem
    ...RankingListViewItem
    ...NormalListViewItem
    ...MoreItem
    ...EventBannerItem
    ...PromotionBannerItem
    ...LineBannerItem
    }

    fragment BannerItem on BannerItem {
    bannerType
    bannerViewType
    thumbnail
    videoUrl
    badgeList
    statusBadge
    titleImage
    title
    altText
    metaList
    caption
    scheme
    seriesId
    eventLog {
        ...EventLogFragment
    }
    discountRate
    discountRateText
    backgroundColor
    characterImage
    }

    fragment OnAirItem on OnAirItem {
    thumbnail
    videoUrl
    titleImage
    title
    subtitleList
    caption
    scheme
    }

    fragment CardViewItem on CardViewItem {
    title
    altText
    thumbnail
    scheme
    badgeList
    ageGradeBadge
    statusBadge
    ageGrade
    selfCensorship
    subtitleList
    caption
    rank
    rankVariation
    isEventBanner
    categoryType
    discountRate
    discountRateText
    backgroundColor
    isBook
    isLegacy
    cardCover {
        ...CardCoverFragment
    }
    eventLog {
        ...EventLogFragment
    }
    }

    fragment CardCoverFragment on CardCover {
    coverImg
    coverRestricted
    }

    fragment CleanViewItem on CleanViewItem {
    id
    type
    showPlayerIcon
    scheme
    title
    thumbnail
    badgeList
    ageGradeBadge
    statusBadge
    subtitleList
    rank
    ageGrade
    selfCensorship
    eventLog {
        ...EventLogFragment
    }
    discountRate
    discountRateText
    }

    fragment PosterViewItem on PosterViewItem {
    id
    type
    showPlayerIcon
    scheme
    title
    altText
    thumbnail
    badgeList
    labelBadgeList
    ageGradeBadge
    statusBadge
    subtitleList
    rank
    rankVariation
    ageGrade
    selfCensorship
    eventLog {
        ...EventLogFragment
    }
    seriesId
    showDimmedThumbnail
    discountRate
    discountRateText
    }

    fragment StrategyViewItem on StrategyViewItem {
    id
    title
    count
    scheme
    }

    fragment RankingListViewItem on RankingListViewItem {
    title
    thumbnail
    badgeList
    ageGradeBadge
    statusBadge
    ageGrade
    selfCensorship
    metaList
    descriptionList
    scheme
    rank
    eventLog {
        ...EventLogFragment
    }
    discountRate
    discountRateText
    }

    fragment NormalListViewItem on NormalListViewItem {
    id
    type
    altText
    ticketUid
    thumbnail
    badgeList
    ageGradeBadge
    statusBadge
    ageGrade
    isAlaramOn
    row1
    row2
    row3 {
        id
        metaList
    }
    row4
    row5
    scheme
    continueScheme
    nextProductScheme
    continueData {
        ...ContinueInfoFragment
    }
    seriesId
    isCheckMode
    isChecked
    isReceived
    isHelixGift
    price
    discountPrice
    discountRate
    discountRateText
    showPlayerIcon
    rank
    isSingle
    singleSlideType
    ageGrade
    selfCensorship
    eventLog {
        ...EventLogFragment
    }
    giftEventLog {
        ...EventLogFragment
    }
    }

    fragment ContinueInfoFragment on ContinueInfo {
    title
    isFree
    productId
    lastReadProductId
    scheme
    continueProductType
    hasNewSingle
    hasUnreadSingle
    }

    fragment MoreItem on MoreItem {
    id
    scheme
    title
    }

    fragment EventBannerItem on EventBannerItem {
    bannerType
    thumbnail
    videoUrl
    titleImage
    title
    subtitleList
    caption
    scheme
    eventLog {
        ...EventLogFragment
    }
    }

    fragment LineBannerItem on LineBannerItem {
    title
    scheme
    subTitle
    bgColor
    rightImage
    eventLog {
        ...EventLogFragment
    }
    }

    fragment Group on Group {
    id
    ... on ListViewGroup {
        meta {
        title
        count
        }
    }
    ... on CardViewGroup {
        meta {
        title
        count
        }
    }
    ... on PosterViewGroup {
        meta {
        title
        count
        }
    }
    type
    dataKey
    groups {
        ...GroupInGroup
    }
    items {
        ...Item
    }
    }

    fragment GroupInGroup on Group {
    id
    type
    dataKey
    items {
        ...Item
    }
    ... on ListViewGroup {
        meta {
        title
        count
        }
    }
    ... on CardViewGroup {
        meta {
        title
        count
        }
    }
    ... on PosterViewGroup {
        meta {
        title
        count
        }
    }
    }
    """

    def crawl_all_webtoons_pagination():
        # print("🚀 전체 웹툰 목록(페이지네이션 포함) 수집 시작...")

        for day_code in DAY_CODES:
            current_page = 0
            is_end = False
            collected_count = 0 
            
            pbar = tqdm(desc=f"[{DAY_NAMES[day_code]}요일] 수집 중", unit="page")
            
            while not is_end:
                try:
                    # 쿼리 전체 구성
                    payload = {
                        "query": FULL_QUERY_STRING, # 위에서 정의한 긴 문자열
                        "variables": {
                            "queryInput": {
                                "categoryUid": 10,
                                "dayTabUid": str(day_code),
                                "type": "Layout",
                                "screenUid": 52,
                                "page": current_page, # 페이지 변수 추가
                                "size": 30
                            }
                        }
                    }
                    
                    response = requests.post(
                        REQUEST_URL, 
                        headers=HEADERS, 
                        data=json.dumps(payload)
                    )
                    response.raise_for_status()
                    data = response.json()

                    sections = data.get('data', {}).get('staticLandingDayOfWeekLayout', {}).get('sections', [])
                    
                    if not sections:
                        break
                    
                    main_section = sections[0]
                    
                    # 종료 조건 확인
                    is_end = main_section.get('isEnd', True)
                    
                    # 아이템 추출
                    items_found_in_page = 0
                    for group in main_section.get('groups', []):
                        for item in group.get('items', []):
                            if item.get('type') == 'CardView':
                                is_up = item.get('statusBadge')
                                series_id = item.get('eventLog', {}).get('eventMeta', {}).get('series_id')
                                if series_id:
                                    main_webtoon_list.append({
                                        'series_id': int(series_id),
                                        'title': item.get('title'),
                                        'url': f'https://page.kakao.com/content/{series_id}',
                                        'category': item.get('eventLog', {}).get('eventMeta', {}).get('subcategory'),
                                        'views': item.get('subtitleList', [None])[0],
                                        'weekday': DAY_NAMES[day_code],
                                        'up': is_up,
                                    })
                                    all_series_ids.add(int(series_id))
                                    items_found_in_page += 1
                    
                    collected_count += items_found_in_page
                    pbar.update(1)
                    pbar.set_postfix({'누적': collected_count})
                    
                    current_page += 1
                    time.sleep(0.3) # 0.3초 대기 (서버 예의 지키기)
                    
                except Exception as e:
                    print(f"\nError on {DAY_NAMES[day_code]} page {current_page}: {e}")
                    # 에러 발생 시 반복문 탈출
                    break
            
            pbar.close()

    # --- 최종 저장될 리스트 (DF 역할을 할 딕셔너리 리스트) ---
    author_role_list = []       # 작가/그림 작가/원작 작가 정보
    keyword_list = []           # 키워드 정보 저장용 리스트

    # 요일 코드: 1=월, 2=화, ..., 7=일 (dayTabUid)
    DAY_CODES = range(1, 8) 
    DAY_NAMES = {1: '월', 2: '화', 3: '수', 4: '목', 5: '금', 6: '토', 7: '일'}

    # --- 상세 정보 크롤링 함수 (줄거리, 작가 정보 수집) ---
    def crawl_detail_info():
        """수집된 모든 series_id에 대해 상세 정보를 크롤링합니다."""
        # print("\n🚀 2단계: 상세 정보 크롤링 시작...")

        detail_query = {
            "query":"\n    query contentHomeInfo($seriesId: Long!) {\n  contentHomeInfo(seriesId: $seriesId) {\n    about {\n      id\n      themeKeywordList {\n        uid\n        title\n        scheme\n      }\n      description\n      screenshotList\n      authorList {\n        id\n        name\n        role\n        roleDisplayName\n      }\n      detail {\n        id\n        publisherName\n        retailPrice\n        ageGrade\n        category\n        rank\n      }\n      guideTitle\n      characterList {\n        thumbnail\n        name\n        description\n      }\n      detailInfoList {\n        title\n        info\n      }\n    }\n    recommend {\n      id\n      seriesId\n      list {\n        ...ContentRecommendGroup\n      }\n    }\n  }\n}\n    \n    fragment ContentRecommendGroup on ContentRecommendGroup {\n  id\n  impLabel\n  type\n  title\n  description\n  items {\n    id\n    type\n    ...PosterViewItem\n  }\n}\n    \n\n    fragment PosterViewItem on PosterViewItem {\n  id\n  type\n  showPlayerIcon\n  scheme\n  title\n  altText\n  thumbnail\n  badgeList\n  labelBadgeList\n  ageGradeBadge\n  statusBadge\n  subtitleList\n  rank\n  rankVariation\n  ageGrade\n  selfCensorship\n  eventLog {\n    ...EventLogFragment\n  }\n  seriesId\n  showDimmedThumbnail\n  discountRate\n  discountRateText\n}\n    \n\n    fragment EventLogFragment on EventLog {\n  fromGraphql\n  click {\n    layer1\n    layer2\n    setnum\n    ordnum\n    copy\n    imp_id\n    imp_provider\n  }\n  eventMeta {\n    id\n    name\n    subcategory\n    category\n    series\n    provider\n    series_id\n    type\n  }\n  viewimp_contents {\n    type\n    name\n    id\n    imp_area_ordnum\n    imp_id\n    imp_provider\n    imp_type\n    layer1\n    layer2\n  }\n  customProps {\n    landing_path\n    view_type\n    helix_id\n    helix_yn\n    helix_seed\n    content_cnt\n    event_series_id\n    event_ticket_type\n    play_url\n    banner_uid\n  }\n}\n    ",
            # 실제 상세 쿼리 (제공해주신 것)의 핵심만 남김
            "variables": {"seriesId": 0} # 여기에 series_id 삽입
        }

        # 상세 정보 저장을 위한 임시 리스트
        temp_detail_list = [] 
        
        # 중복 ID는 한 번만 처리
        for series_id in tqdm(list(all_series_ids), desc="상세 정보 수집 중"):
            try:
                detail_query["variables"]["seriesId"] = series_id
                
                response = requests.post(
                    REQUEST_URL, 
                    headers=HEADERS, 
                    data=json.dumps(detail_query)
                )
                response.raise_for_status()
                data = response.json()
                
                about_data = data.get('data', {}).get('contentHomeInfo', {}).get('about', {})

                if about_data:
                    # A. 줄거리 등 메인 정보 (나중에 Webtoon_DF에 병합)
                    temp_detail_list.append({
                        'series_id': series_id,
                        'description': about_data.get('description', '설명 없음').replace('\\n', '\n'),
                        'publisher': about_data.get('detail', {}).get('publisherName'),
                        'age_limit': about_data.get('detail', {}).get('ageGrade'),
                    })
                    
                    # B. 작가 역할별 정보 (Author_DF 생성)
                    for author in about_data.get('authorList', []):
                        author_role_list.append({
                            'series_id': series_id,
                            'author_id': author.get('id', 'N/A'),
                            'name': author.get('name'),
                            'role': author.get('role'),             # Writer, Painter, Original 등
                            'role_display': author.get('roleDisplayName')
                        })
                
                    # C. 키워드 정보 저장
                    for keyword in about_data.get('themeKeywordList', []):
                        keyword_list.append({
                            'series_id': series_id,
                            'keyword_title': keyword.get('title'),
                        })
                
                # 짧은 지연 시간을 두어 서버 부하를 줄임
                time.sleep(0.1) 
                
            except Exception as e:
                print(f"[{series_id}] 상세 크롤링 오류 발생: {e}")
                time.sleep(1) # 에러 시 지연 시간을 늘려 임시 차단 방지

        return temp_detail_list

        
    # 1단계 실행: 요일별 목록 수집
    crawl_all_webtoons_pagination()
    
    # 2단계 실행: 상세 정보 수집
    detail_data_list = crawl_detail_info()
    
    # --- 3. 데이터프레임 구조에 맞게 최종 정리 ---
    
    # 1. Webtoon_DF: 메인 목록 + 상세 정보(줄거리 등) 병합
    final_webtoon_df = []
    description_map = {item['series_id']: item for item in detail_data_list}
    
    for webtoon in main_webtoon_list:
        series_id = webtoon['series_id']
        detail = description_map.get(series_id, {})
        
        # 상세 정보 필드를 메인 웹툰 정보에 추가
        webtoon['description'] = detail.get('description')
        webtoon['publisher'] = detail.get('publisher')
        webtoon['age_limit_detail'] = detail.get('age_limit')
        final_webtoon_df.append(webtoon)

    # 2. Author_DF: 작가 정보
    final_author_df = author_role_list
        
    # --- 최종 저장될 리스트 (DF 역할을 할 딕셔너리 리스트) ---
    thumbnail_list = []      # 웹툰 메인 정보 + 썸네일 (나중에 병합됨)

    # --- 썸네일 이미지 크롤링 함수 ---
    def crawl_thumbnail_info():
        """수집된 모든 series_id에 대해 썸네일 이미지 크롤링합니다."""
        print("\n🚀 2단계: 썸네일 이미지 크롤링 시작...")

        detail_query = {
            "query":"\n    query contentHomeOverview($seriesId: Long!) {\n  contentHomeOverview(seriesId: $seriesId) {\n    id\n    seriesId\n    displayAd {\n      ...DisplayAd\n      ...DisplayAd\n    }\n    content {\n      ...SeriesFragment\n    }\n    displayAd {\n      ...DisplayAd\n    }\n    lastNoticeDate\n    setList {\n      ...NormalListViewItem\n    }\n    relatedSeries {\n      ...SeriesFragment\n    }\n  }\n}\n    \n    fragment DisplayAd on DisplayAd {\n  sectionUid\n  bannerUid\n  treviUid\n  momentUid\n}\n    \n\n    fragment SeriesFragment on Series {\n  id\n  seriesId\n  title\n  thumbnail\n  landThumbnail\n  categoryUid\n  lang\n  category\n  categoryType\n  subcategoryUid\n  subcategory\n  badge\n  isAllFree\n  isWaitfree\n  ageGrade\n  state\n  onIssue\n  authors\n  description\n  pubPeriod\n  freeSlideCount\n  lastSlideAddedDate\n  waitfreeBlockCount\n  waitfreePeriodByMinute\n  bm\n  saleState\n  startSaleDt\n  saleMethod\n  discountRate\n  discountRateText\n  serviceProperty {\n    ...ServicePropertyFragment\n  }\n  operatorProperty {\n    ...OperatorPropertyFragment\n  }\n  assetProperty {\n    ...AssetPropertyFragment\n  }\n  translateProperty {\n    ...TranslatePropertyFragment\n  }\n}\n    \n\n    fragment ServicePropertyFragment on ServiceProperty {\n  viewCount\n  readCount\n  ratingCount\n  ratingSum\n  commentCount\n  pageContinue {\n    ...ContinueInfoFragment\n  }\n  todayGift {\n    ...TodayGift\n  }\n  preview {\n    ...PreviewFragment\n    ...PreviewFragment\n  }\n  waitfreeTicket {\n    ...WaitfreeTicketFragment\n  }\n  isAlarmOn\n  isLikeOn\n  ticketCount\n  purchasedDate\n  lastViewInfo {\n    ...LastViewInfoFragment\n  }\n  purchaseInfo {\n    ...PurchaseInfoFragment\n  }\n  preview {\n    ...PreviewFragment\n  }\n  ticketInfo {\n    price\n    discountPrice\n    ticketType\n  }\n}\n    \n\n    fragment ContinueInfoFragment on ContinueInfo {\n  title\n  isFree\n  productId\n  lastReadProductId\n  scheme\n  continueProductType\n  hasNewSingle\n  hasUnreadSingle\n}\n    \n\n    fragment TodayGift on TodayGift {\n  id\n  uid\n  ticketType\n  ticketKind\n  ticketCount\n  ticketExpireAt\n  ticketExpiredText\n  isReceived\n  seriesId\n}\n    \n\n    fragment PreviewFragment on Preview {\n  item {\n    ...PreviewSingleFragment\n  }\n  nextItem {\n    ...PreviewSingleFragment\n  }\n  usingScroll\n}\n    \n\n    fragment PreviewSingleFragment on Single {\n  id\n  productId\n  seriesId\n  title\n  thumbnail\n  badge\n  isFree\n  ageGrade\n  state\n  slideType\n  lastReleasedDate\n  size\n  pageCount\n  isHidden\n  remainText\n  isWaitfreeBlocked\n  saleState\n  operatorProperty {\n    ...OperatorPropertyFragment\n  }\n  assetProperty {\n    ...AssetPropertyFragment\n  }\n}\n    \n\n    fragment OperatorPropertyFragment on OperatorProperty {\n  thumbnail\n  copy\n  helixImpId\n  isTextViewer\n  selfCensorship\n  isBook\n  cashInfo {\n    discountRate\n    setDiscountRate\n  }\n  ticketInfo {\n    price\n    discountPrice\n    ticketType\n  }\n}\n    \n\n    fragment AssetPropertyFragment on AssetProperty {\n  bannerImage\n  cardImage\n  cardTextImage\n  cleanImage\n  ipxVideo\n  bannerSet {\n    ...BannerSetFragment\n  }\n  cardSet {\n    ...CardSetFragment\n  }\n  cardCover {\n    ...CardCoverFragment\n  }\n}\n    \n\n    fragment BannerSetFragment on BannerSet {\n  backgroundImage\n  backgroundColor\n  mainImage\n  titleImage\n}\n    \n\n    fragment CardSetFragment on CardSet {\n  backgroundColor\n  backgroundImage\n}\n    \n\n    fragment CardCoverFragment on CardCover {\n  coverImg\n  coverRestricted\n}\n    \n\n    fragment WaitfreeTicketFragment on WaitfreeTicket {\n  chargedPeriod\n  chargedCount\n  chargedAt\n}\n    \n\n    fragment LastViewInfoFragment on LastViewInfo {\n  isDone\n  lastViewDate\n  rate\n  spineIndex\n}\n    \n\n    fragment PurchaseInfoFragment on PurchaseInfo {\n  purchaseType\n  rentExpireDate\n  expired\n}\n    \n\n    fragment TranslatePropertyFragment on TranslateProperty {\n  category {\n    ...LocaleMapFragment\n  }\n  sub_category {\n    ...LocaleMapFragment\n  }\n}\n    \n\n    fragment LocaleMapFragment on LocaleMap {\n  ko\n  en\n  th\n}\n    \n\n    fragment NormalListViewItem on NormalListViewItem {\n  id\n  type\n  altText\n  ticketUid\n  thumbnail\n  badgeList\n  ageGradeBadge\n  statusBadge\n  ageGrade\n  isAlaramOn\n  row1\n  row2\n  row3 {\n    id\n    metaList\n  }\n  row4\n  row5\n  scheme\n  continueScheme\n  nextProductScheme\n  continueData {\n    ...ContinueInfoFragment\n  }\n  seriesId\n  isCheckMode\n  isChecked\n  isReceived\n  isHelixGift\n  price\n  discountPrice\n  discountRate\n  discountRateText\n  showPlayerIcon\n  rank\n  isSingle\n  singleSlideType\n  ageGrade\n  selfCensorship\n  eventLog {\n    ...EventLogFragment\n  }\n  giftEventLog {\n    ...EventLogFragment\n  }\n}\n    \n\n    fragment EventLogFragment on EventLog {\n  fromGraphql\n  click {\n    layer1\n    layer2\n    setnum\n    ordnum\n    copy\n    imp_id\n    imp_provider\n  }\n  eventMeta {\n    id\n    name\n    subcategory\n    category\n    series\n    provider\n    series_id\n    type\n  }\n  viewimp_contents {\n    type\n    name\n    id\n    imp_area_ordnum\n    imp_id\n    imp_provider\n    imp_type\n    layer1\n    layer2\n  }\n  customProps {\n    landing_path\n    view_type\n    helix_id\n    helix_yn\n    helix_seed\n    content_cnt\n    event_series_id\n    event_ticket_type\n    play_url\n    banner_uid\n  }\n}\n    ",
            "variables":{"seriesId":0}
        }
        
            # 썸네일 이미지 저장을 위한 임시 리스트
        temp_detail_list = [] 
        
        # 중복 ID는 한 번만 처리
        for series_id in tqdm(list(all_series_ids), desc="썸네일 이미지 수집 중"):
            try:
                detail_query["variables"]["seriesId"] = series_id
                
                response = requests.post(
                    REQUEST_URL, 
                    headers=HEADERS, 
                    data=json.dumps(detail_query)
                )
                response.raise_for_status()
                data = response.json()
                
                thumbnail = data.get('data', {}).get('contentHomeOverview', {}).get('content', {}).get("thumbnail")
                
                if thumbnail:
                    # A. 줄거리 등 메인 정보 (나중에 Webtoon_DF에 병합)
                    temp_detail_list.append({
                        'series_id': series_id,
                        'thumbnail': thumbnail,
                    })
                
                # 짧은 지연 시간을 두어 서버 부하를 줄임
                time.sleep(0.1) 
                
            except Exception as e:
                print(f"[{series_id}] 상세 크롤링 오류 발생: {e}")
                time.sleep(1) # 에러 시 지연 시간을 늘려 임시 차단 방지

        return temp_detail_list

    thumbnail_data_list = crawl_thumbnail_info()
    # --- 3. 데이터프레임 구조에 맞게 최종 정리 ---
    
    # 1. Webtoon_DF: 메인 목록 + 썸네일 url 병합
    description_map = {item['series_id']: item for item in thumbnail_data_list}
    
    for webtoon in main_webtoon_list:
        series_id = webtoon['series_id']
        thumbnail = description_map.get(series_id, {})
        
        # 상세 정보 필드를 메인 웹툰 정보에 추가
        webtoon['thumbnailUrl'] = thumbnail.get('thumbnail')
        final_webtoon_df.append(webtoon)
        
    by_series = defaultdict(list)
    for item in keyword_list:
        sid = item["series_id"]
        kw  = item["keyword_title"]
        by_series[sid].append(kw)

    rows = []
    for sid, kws in by_series.items():
        rows.append({
            "series_id": sid,
            "keywords": ", ".join(kws),   # 리스트 그대로 두고 싶으면 kws 로
        })
        
    df_keywords = pd.DataFrame(rows).sort_values("series_id").reset_index(drop=True)
    
    # (가정) 이전에 성공적으로 수집된 final_author_df 사용
    Author_DF_Raw = pd.DataFrame(final_author_df)

    def split_and_clean_authors_final_v3(df, role_key):
        """
        논리 순서를 완벽하게 수정한 버전입니다.
        1. 분리 -> 2. 기존 컬럼 삭제 -> 3. 컬럼명 변경
        """
        # 1. 역할 필터링
        filtered_df = df[df['role'] == role_key].copy()
        
        # 2. 이름 분리 (임시 컬럼 'name_temp' 생성)
        filtered_df['name_temp'] = filtered_df['name'].str.split(', ')
        
        # 3. 행 분리 (Explode)
        exploded_df = filtered_df.explode('name_temp').reset_index(drop=True)
        
        # 4. [중요] 불필요한 기존 컬럼 먼저 삭제
        # - 'name': 콤마로 뭉쳐있던 원본 이름
        # - 'author_id': UUID 에러가 났던 식별자
        exploded_df = exploded_df.drop(columns=['name', 'author_id'])
        
        # 5. [중요] 임시 컬럼의 이름을 최종 이름('name')으로 변경
        final_df = exploded_df.rename(columns={'name_temp': 'name'})
        
        # 6. 컬럼 순서 정렬
        return final_df[['series_id', 'name', 'role', 'role_display']]

    # 1. 글 작가
    Writer_DF = split_and_clean_authors_final_v3(Author_DF_Raw, 'writer')

    # 2. 그림 작가
    Painter_DF = split_and_clean_authors_final_v3(Author_DF_Raw, 'illustrator')

    # 3. 원작 작가
    Original_Author_DF = split_and_clean_authors_final_v3(Author_DF_Raw, 'original_author')
    
    kp_df = pd.DataFrame(final_webtoon_df)
    
    # Up 뱃지가 있으면 Up 된 웹툰
    kp_df['up'] = np.where(kp_df['up']=="BadgeNewStatic", True, False)
    
    df_merged = (
        kp_df.groupby(
            ["series_id", "title", "url", "category", "views",
            "thumbnailUrl", "up","description", "publisher", "age_limit_detail"],
            as_index=False
        )["weekday"]
        .agg(lambda s: ", ".join(sorted(set(s))))
    )
    
    kp_final_df = df_merged.merge(df_keywords, on="series_id", how="left")

    def combine_cat(row):
        base = str(row["category"]).strip()           # 예: "로판"
        kws  = str(row["keywords"]).strip()
        if not kws or kws == "nan":
            return base
        return f"{base}, {kws}"

    kp_final_df["category"] = kp_final_df.apply(combine_cat, axis=1)

    # 필요하면 keywords 컬럼은 드롭
    kp_final_df = kp_final_df.drop(columns=["keywords"])
    
    wirters_pivot = (
        Writer_DF
        .groupby(["series_id", "role"])["name"]
        .agg(lambda s: ", ".join(sorted(set(s))))
        .unstack(fill_value="")         # role을 컬럼으로 피벗
        .reset_index()
    )

    kp_final_df = kp_final_df.merge(wirters_pivot, on="series_id", how="left")
    
    painters_pivot = (
        Painter_DF
        .groupby(["series_id", "role"])["name"]
        .agg(lambda s: ", ".join(sorted(set(s))))
        .unstack(fill_value="")         # role을 컬럼으로 피벗
        .reset_index()
    )

    kp_final_df = kp_final_df.merge(painters_pivot, on="series_id", how="left")
    
    original_pivot = (
        Original_Author_DF
        .groupby(["series_id", "role"])["name"]
        .agg(lambda s: ", ".join(sorted(set(s))))
        .unstack(fill_value="")         # role을 컬럼으로 피벗
        .reset_index()
    )

    kp_final_df = kp_final_df.merge(original_pivot, on="series_id", how="left")
    
    kp_final_df2 = kp_final_df.drop(["views", "publisher"], axis=1)
    
    kpage = kp_final_df2.rename(columns={
        "series_id": "titleId",
        "title": "titleName",
        "url": "Url",
        "thumbnailUrl": "thumbnailUrl",
        "description": "synopsis",
        "writer": "Writer",
        "illustrator": "Painter",
        "original_author": "Original",
        "category": "genre",
        "weekday": "day",
        'up': 'is_up'
    })

    adult_map = {"All": False, "Fifteen": False, "Nineteen": True}
    kpage["is_adult"] = kpage["age_limit_detail"].map(adult_map).fillna(False)

    kpage = kpage[["titleId","titleName","Url","thumbnailUrl","is_adult",
                "Writer","Painter","Original","synopsis","genre","day","is_up"]]
    kpage["provider"] = "KAKAOPAGE"
    
    return kpage

# 플랫폼별 크롤링 메인 함수 (이 함수가 스레드 풀에서 동시에 실행됨)
def crawl_platform_data(platform_name):
    print(f"[{platform_name}] 크롤링 시작...")
    
    try:
        if platform_name == "NAVER":
            # (내부적으로 상세 크롤링 병렬 처리 및 데이터 클렌징 후) DataFrame 반환
            result_df = Naver_webtoon_crawler() 
        elif platform_name == "KAKAO":
            result_df = Kakao_webtoon_crawler()
        elif platform_name == "KAKAOPAGE":
            result_df = Kpage_webtoon_crawler()
        else:
            return pd.DataFrame()

        # 서버 부하 방지 (중요!)
        # 크롤링 완료 후 잠시 대기
        time.sleep(1) 
        
        print(f"[{platform_name}] 크롤링 완료. 수집된 웹툰 개수: {len(result_df)}")
        return result_df # DataFrame 객체를 반환합니다.
        
    except Exception as e:
        print(f"[{platform_name}] 크롤링 중 오류 발생: {e}")
        return pd.DataFrame() # 오류 발생 시 빈 DataFrame 반환

def run_concurrent_crawling():
    platforms = ["NAVER", "KAKAO", "KAKAOPAGE"]
    
    # max_workers: 3개 플랫폼을 동시에 시작 (최대 3개의 메인 스레드)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        
        # 각 플랫폼별 크롤링 작업을 스레드 풀에 할당
        futures = {executor.submit(crawl_platform_data, p): p for p in platforms}
        
        all_results_dfs = []
        
        # 작업이 완료되는 순서대로 결과를 수집합니다.
        for future in concurrent.futures.as_completed(futures):
            platform_name = futures[future]
            try:
                # 결과는 DataFrame 객체입니다.
                result_df = future.result() 
                
                if not result_df.empty:
                    all_results_dfs.append(result_df)
                    print(f"데이터 수집 완료: {platform_name} (총 {len(result_df)}개)")
                else:
                    print(f"데이터 수집 실패 또는 결과 없음: {platform_name}")
                    
            except Exception as exc:
                print(f"[{platform_name}] 결과 처리 중 오류 발생: {exc}")

    # 2. 결과 통합 (모든 병렬 작업 완료 후)
    if all_results_dfs:
        # Pandas의 concat 함수를 사용하여 모든 DataFrame을 수직으로 결합합니다.
        final_integrated_df = pd.concat(all_results_dfs, ignore_index=True)
        print(f"\n✅ 최종 데이터 통합 완료. 총 웹툰 개수: {len(final_integrated_df)}")
        return final_integrated_df
    else:
        print("\n❌ 최종 통합할 데이터가 없습니다.")
        return pd.DataFrame()

# # 실행 예시: 
if __name__ == '__main__':
    # (실제 실행 시에는 process_xxx_webtoons 함수가 정의되어 있어야 합니다.)
    final_df = run_concurrent_crawling()

    prov_agg = (
        final_df
        .groupby("titleName", as_index=False)["provider"]
        .agg(lambda s: ", ".join(sorted(set(s))))
    )
    
    # 우선순위 컬럼 추가: KAKAOPAGE(2) > KAKAO(1) > 나머지(0)
    priority_map = {"KAKAOPAGE": 2, "KAKAO": 1}
    final_df["provider_priority"] = final_df["provider"].map(priority_map).fillna(0)

    # 제목별로 우선순위 가장 높은 행 하나만 남기기
    base_agg = (
        final_df
        .sort_values("provider_priority", ascending=False)
        .groupby("titleName", as_index=False)
        .first()   # 같은 제목 안에서 priority 높은 행이 먼저 오므로 그걸 사용
    )

    # priority 컬럼은 이제 필요 없으니 제거
    base_agg = base_agg.drop(columns=["provider_priority"])
    
    all_webtoons = base_agg.drop(columns=["provider"]).merge(
        prov_agg,
        on="titleName",
        how="left",
    )
    
    all_webtoons = all_webtoons.drop(['titleId'], axis=1)
    
    # JSON 파일 저장
    # orient='records': 각 행을 JSON 객체로 만들어 리스트 형태로 저장 (웹 API에 가장 적합한 형태)
    try:
        all_webtoons.to_json(
            "final_webtoon.json", 
            orient='records', 
            indent=4, 
            force_ascii=False # 한글 깨짐 방지
        )
    except Exception as e:
        print(f"❌ JSON 파일 저장 중 오류 발생: {e}")
        
    print(all_webtoons.head())