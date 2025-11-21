from django.shortcuts import render
from django.db.models import Q
import requests
from .models import Webtoon

PLATFORM_API = {
    'NAVER': 'https://korea-webtoon-api.onrender.com/webtoons?provider=NAVER&page=1&perPage=100&sort=ASC',
    'KAKAO': 'https://korea-webtoon-api.onrender.com/webtoons?provider=KAKAO&page=1&perPage=100&sort=ASC',
    'KAKAO_PAGE': 'https://korea-webtoon-api.onrender.com/webtoons?provider=KAKAO_PAGE&page=1&perPage=100&sort=ASC'
}

def fetch_webtoons_all_pages(provider):
    all_webtoons = []
    for page in range(1, 51):
        url = f'https://korea-webtoon-api.onrender.com/webtoons?provider={provider}&page={page}&perPage=100&sort=ASC'
        resp = requests.get(url)
        page_items = resp.json().get('webtoons', [])
        # 빈 페이지라면 더 이상 요청하지 않음
        if not page_items:
            break
        all_webtoons.extend(page_items)
    return all_webtoons

def filter_webtoons_with_updateDays(webtoons):
    # 업데이트 요일이 하나 이상 존재하는 웹툰만 남김
    return [toon for toon in webtoons if toon.get('updateDays')]

def sync_webtoons(provider):
    all_webtoons = fetch_webtoons_all_pages(provider)
    valid_webtoons = filter_webtoons_with_updateDays(all_webtoons)
    # 이미 저장된 웹툰은 중복 저장 방지
    for toon in valid_webtoons:
        Webtoon.objects.update_or_create(
            url=toon['url'],
            defaults={
                'provider': provider,
                'title': toon['title'].strip(),
                'authors': ','.join(toon.get('authors', [])),
                'update_days': ','.join(toon['updateDays']),
                'thumbnail': toon['thumbnail'][0] if toon.get('thumbnail') else '',
                'is_end': toon['isEnd'],
            }
        )

def webtoon_list(request):
    platform = request.GET.get('platform', 'NAVER')
    query = request.GET.get('q', '')
    
    # [1] DB에 플랫폼별 웹툰이 없으면 API로 불러와서 동기화/저장
    if not Webtoon.objects.filter(provider=platform).exists():
        sync_webtoons(platform)

    # [2] DB에서 검색·필터링
    qs = Webtoon.objects.filter(provider=platform).exclude(update_days='')
    
    if platform in ['KAKAO', 'KAKAO_PAGE']:
        qs = qs.filter(is_end=False)

    if query:
        qs = qs.filter(
            Q(title__icontains=query) |
            Q(authors__icontains=query)
        )

    webtoons = qs.all()
    return render(request, 'toons/index.html', {
        'webtoons': webtoons,
        'platform': platform,
        'query': query,
    })
