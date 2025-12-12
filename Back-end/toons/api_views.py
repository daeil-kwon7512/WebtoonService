from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Webtoon, Genre
from .serializers import WebtoonSerializer
import requests
from django.core.paginator import Paginator
import pandas as pd
from django.conf import settings
from pathlib import Path

# PLATFORM_API = {
#     'NAVER': 'https://korea-webtoon-api.onrender.com/webtoons?provider=NAVER&page={page}&perPage=100&sort=ASC',
#     'KAKAO': 'https://korea-webtoon-api.onrender.com/webtoons?provider=KAKAO&page={page}&perPage=100&sort=ASC',
#     'KAKAO_PAGE': 'https://korea-webtoon-api.onrender.com/webtoons?provider=KAKAO_PAGE&page={page}&perPage=100&sort=ASC'
# }

# def sync_webtoons(provider):
#     """외부 API에서 웹툰 데이터 가져와서 DB에 저장"""
#     for page in range(1, 51):  # 1~50페이지
#         url = PLATFORM_API[provider].format(page=page)
#         try:
#             response = requests.get(url, timeout=10)
#             data = response.json()
#             webtoons = data.get('webtoons', [])
            
#             if not webtoons:  # 빈 페이지면 종료
#                 break
            
#             for toon in webtoons:
#                 # updateDays 있는 것만 저장
#                 if not toon.get('updateDays'):
#                     continue
                
#                 Webtoon.objects.update_or_create(
#                     url=toon['url'],
#                     defaults={
#                         'provider': provider,
#                         'title': toon['title'].strip(),
#                         'authors': ', '.join(toon.get('authors', [])),
#                         'update_days': ','.join(toon['updateDays']),
#                         'thumbnail': toon['thumbnail'][0] if toon.get('thumbnail') else '',
#                         'is_end': toon.get('isEnd', False),
#                     }
#                 )
#         except Exception as e:
#             print(f"Error syncing {provider} page {page}: {e}")
#             break
    
#     print(f"{provider} 동기화 완료!")

def import_webtoons_from_csv(csv_path: str):
    df = pd.read_csv(csv_path)
    df = df.fillna('')

    created_count = 0

    for row in df.itertuples(index=False):
        webtoon, created = Webtoon.objects.get_or_create(
            provider=row.provider,
            title=row.titleName,
            url=row.Url,
            defaults={
                'writers': row.Writer,
                'painters': row.Painter,
                'original_author': row.Original,
                'update_days': row.day,
                'thumbnail': row.thumbnailUrl,
                'is_adult': bool(row.is_adult),
                'synopsis': row.synopsis,
                'is_up': bool(row.is_up),
            }
        )

        # 장르 M2M 연결
        genre_text = row.genre
        if genre_text:
            names = [g.strip() for g in str(genre_text).split(',') if g.strip()]
            for name in names:
                genre_obj, _ = Genre.objects.get_or_create(tag=name)
                webtoon.genres.add(genre_obj)

        if created:
            created_count += 1

    return created_count

@api_view(['GET'])
@permission_classes([AllowAny])
def webtoon_list(request):
    """웹툰 목록 조회 (페이징 추가)"""
    provider = request.GET.get('provider', 'NAVER')
    q = request.GET.get('q', '')
    page_num = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 100))  # 한 페이지에 100개씩
    
    # ✅ OS/경로에 상관없이 CSV 파일 위치 지정 (BASE_DIR 기준)
    csv_path = Path(settings.BASE_DIR) / "crawling" / "all_webtoons.csv"
    
    # DB에 해당 플랫폼 웹툰이 없으면 동기화
    if not Webtoon.objects.filter(provider=provider).exists():
        if not csv_path.exists():
            # 파일이 없을 때 500 대신 좀 더 친절한 에러를 줄 수도 있음
            return Response(
                {"detail": f"CSV 파일을 찾을 수 없습니다: {csv_path}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Path 객체를 문자열로 변환해서 전달 (함수 구현에 따라 str() 필요할 수 있음)
        import_webtoons_from_csv(str(csv_path))
    
    webtoons = Webtoon.objects.filter(provider=provider).exclude(update_days='').order_by('-id')
    
    # 카카오/카카오페이지는 연재중만
    # if provider in ['KAKAO', 'KAKAOPAGE']:
    # 성인웹툰은 빼고
    webtoons = webtoons.filter(is_adult=False)
    
    # 검색
    if q:
        webtoons = webtoons.filter(
            Q(title__icontains=q) # | Q(authors__icontains=q)
        )
    
    # 페이징
    paginator = Paginator(webtoons, per_page)
    page_obj = paginator.get_page(page_num)
    
    serializer = WebtoonSerializer(page_obj, many=True, context={'request': request})
    
    return Response({
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page_num,
        'results': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def webtoon_detail(request, webtoon_id):
    """웹툰 상세 조회"""
    try:
        webtoon = Webtoon.objects.get(id=webtoon_id)
    except Webtoon.DoesNotExist:
        return Response({'error': '웹툰을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = WebtoonSerializer(webtoon, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, webtoon_id):
    """즐겨찾기 토글"""
    try:
        webtoon = Webtoon.objects.get(id=webtoon_id)
    except Webtoon.DoesNotExist:
        return Response({'error': '웹툰을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    
    if webtoon.favorited_by.filter(id=request.user.id).exists():
        webtoon.favorited_by.remove(request.user)
        is_favorited = False
        message = '즐겨찾기 해제'
    else:
        webtoon.favorited_by.add(request.user)
        is_favorited = True
        message = '즐겨찾기 추가'
    
    return Response({
        'message': message,
        'is_favorited': is_favorited,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_favorites(request):
    """내 즐겨찾기 목록"""
    provider = request.GET.get('provider')
    q = request.GET.get('q', '')
    
    favorites = request.user.favorite_webtoons.all()
    
    # 플랫폼 필터
    if provider and provider != 'ALL':
        favorites = favorites.filter(provider=provider)
    
    # 검색
    if q:
        favorites = favorites.filter(
            Q(title__icontains=q) | Q(authors__icontains=q)
        )
    
    serializer = WebtoonSerializer(favorites, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
