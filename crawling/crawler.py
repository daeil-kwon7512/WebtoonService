import requests
import pandas as pd
from tqdm import tqdm
import time
import os
from datetime import datetime

# 헤더 설정
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 파일 경로 정의
FILES = {
    'webtoon': "data_webtoon.csv",
    'author': "data_author.csv",
    'genre': "data_genre.csv",
    'tag': "data_tag.csv"
}

def get_today_naver_code():
    """오늘 요일을 네이버 API 파라미터(mon, tue...)로 변환"""
    # 월=0, 화=1, ..., 일=6
    weekday_idx = datetime.now().weekday()
    codes = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    return codes[weekday_idx]

def load_existing_data():
    """기존 CSV 파일이 있으면 불러오고, 없으면 빈 DataFrame 반환"""
    dfs = {}
    for key, path in FILES.items():
        if os.path.exists(path):
            dfs[key] = pd.read_csv(path)
        else:
            # 파일이 없으면 빈 프레임 생성 (컬럼 구조는 나중에 concat할 때 맞춰짐)
            dfs[key] = pd.DataFrame()
    return dfs

def crawl_naver_webtoon_incremental():
    # 1. 기존 데이터 로드
    existing_dfs = load_existing_data()
    
    # 2. 수집할 요일 결정
    if existing_dfs['webtoon'].empty:
        print("🚀 [초기 실행] 데이터 파일이 없어 '모든 요일'을 수집합니다.")
        target_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'dailyPlus']
        is_initial_run = True
        existing_ids = set()
    else:
        today = get_today_naver_code()
        print(f"🔄 [증분 실행] 기존 데이터 발견! '오늘({today})' 연재작만 확인합니다.")
        target_days = [today, 'dailyPlus'] # 오늘은 필수, dailyPlus(매일+)도 확인 추천
        is_initial_run = False
        existing_ids = set(existing_dfs['webtoon']['titleId'].unique())

    # ---------------------------------------------------------
    # 3. 기본 리스트 수집 (타겟 요일만)
    # ---------------------------------------------------------
    print("=== 1. 기본 웹툰 목록 수집 ===")
    
    new_webtoon_list = []
    new_author_list = []
    
    collected_ids = set() # 이번 실행에서 발견한 ID들

    for day_code in tqdm(target_days):
        url = f'https://comic.naver.com/api/webtoon/titlelist/weekday?week={day_code}&order=user'
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                for webtoon in data["titleList"]:
                    t_id = int(webtoon["titleId"])
                    collected_ids.add(t_id)

                    # 이미 있는 웹툰이면 기본 정보만 업데이트하고 스킵할 수도 있음
                    # 여기서는 '새로운 웹툰'만 리스트에 담아서 처리
                    if t_id in existing_ids:
                        continue 

                    # === 신규 웹툰 발견! ===
                    # 1-1. 메인 정보
                    new_webtoon_list.append({
                        "titleId": t_id,
                        "titleName": webtoon["titleName"],
                        "thumbnailUrl": webtoon["thumbnailUrl"],
                        "starScore": float(webtoon["starScore"]),
                        "viewCount": int(webtoon["viewCount"]),
                        "adult": webtoon["adult"],
                        "finish": webtoon["finish"]
                    })
                    
                    # 1-2. 작가 정보
                    writers = [w['name'] for w in webtoon.get("writers", [])]
                    painters = [p['name'] for p in webtoon.get("painters", [])]
                    origins = [o['name'] for o in webtoon.get("novelOriginAuthors", [])]
                    
                    all_authors = list(set(writers + painters + origins))
                    for name in all_authors:
                        new_author_list.append({"titleId": t_id, "authorName": name})
                        
            time.sleep(0.1)
        except Exception as e:
            print(f"Error crawling {day_code}: {e}")

    print(f"👉 금일 확인된 전체 ID 수: {len(collected_ids)}")
    print(f"👉 새로 추가될 신규 웹툰: {len(new_webtoon_list)}개")

    if not new_webtoon_list:
        print("✅ 신규 웹툰이 없습니다. 종료합니다.")
        return

    # 신규 데이터프레임 생성
    df_new_webtoon = pd.DataFrame(new_webtoon_list)
    df_new_author = pd.DataFrame(new_author_list)

    # ---------------------------------------------------------
    # 4. 상세 정보 수집 (신규 웹툰만!)
    # ---------------------------------------------------------
    print("\n=== 2. 신규 웹툰 상세 태그/장르 수집 ===")
    
    genre_list = []
    tag_list = []
    
    session = requests.Session()
    session.headers.update(headers)
    
    # 새로 찾은 웹툰의 ID 목록만 순회
    new_ids = df_new_webtoon['titleId'].unique()
    
    for t_id in tqdm(new_ids):
        url = f'https://comic.naver.com/api/article/list/info?titleId={t_id}'
        try:
            response = session.get(url)
            if response.status_code == 200:
                data = response.json()
                gfp_data = data.get("gfpAdCustomParam", {})
                
                # 장르
                if gfp_data.get("genreTypes"):
                    for g in gfp_data["genreTypes"]:
                        genre_list.append({"titleId": t_id, "genre": g})
                
                # 태그
                if gfp_data.get("tags"):
                    for t in gfp_data["tags"]:
                        tag_list.append({"titleId": t_id, "tag": t})
            
            # time.sleep(0.05)
            
        except Exception as e:
            print(f"Error detail {t_id}: {e}")

    df_new_genre = pd.DataFrame(genre_list)
    df_new_tag = pd.DataFrame(tag_list)
    
    # ---------------------------------------------------------
    # 5. 데이터 병합 및 저장
    # ---------------------------------------------------------
    print("\n=== 3. 데이터 병합 및 저장 ===")

    # 기존 데이터와 합치기 (concat)
    final_dfs = {}
    
    # (1) Webtoon
    if not existing_dfs['webtoon'].empty:
        # 혹시 모를 중복 제거 (기존 것 유지, 새것 추가)
        final_dfs['webtoon'] = pd.concat([existing_dfs['webtoon'], df_new_webtoon]).drop_duplicates(subset=['titleId'], keep='last')
    else:
        final_dfs['webtoon'] = df_new_webtoon

    # (2) Author
    if not existing_dfs['author'].empty:
        final_dfs['author'] = pd.concat([existing_dfs['author'], df_new_author]).drop_duplicates()
    else:
        final_dfs['author'] = df_new_author

    # (3) Genre
    if not existing_dfs['genre'].empty:
        final_dfs['genre'] = pd.concat([existing_dfs['genre'], df_new_genre]).drop_duplicates()
    else:
        final_dfs['genre'] = df_new_genre
        
    # (4) Tag
    if not existing_dfs['tag'].empty:
        final_dfs['tag'] = pd.concat([existing_dfs['tag'], df_new_tag]).drop_duplicates()
    else:
        final_dfs['tag'] = df_new_tag

    # 파일로 저장
    for key, path in FILES.items():
        if not final_dfs[key].empty:
            final_dfs[key].to_csv(path, index=False)
            print(f"- {path} 저장 완료 ({len(final_dfs[key])}행)")
        else:
            print(f"- {key} 데이터가 없어 저장하지 않습니다.")

    print("\n🎉 크롤링 및 데이터 업데이트 완료!")

if __name__ == "__main__":
    crawl_naver_webtoon_incremental()