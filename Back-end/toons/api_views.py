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
    """웹툰 목록 조회"""
    # ✅ OS/경로에 상관없이 CSV 파일 위치 지정 (BASE_DIR 기준)
    csv_path = Path(settings.BASE_DIR) / "crawling" / "all_webtoons.csv"
    
    if not csv_path.exists():
        # 파일이 없을 때 500 대신 좀 더 친절한 에러를 줄 수도 있음
        return Response(
            {"detail": f"CSV 파일을 찾을 수 없습니다: {csv_path}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Path 객체를 문자열로 변환해서 전달 (함수 구현에 따라 str() 필요할 수 있음)
    # import_webtoons_from_csv(str(csv_path))
       
    q = request.GET.get('q', '').strip()
    
    # DB에서 조회
    webtoons = Webtoon.objects.all()   
    
    # 성인웹툰은 빼고
    webtoons = webtoons.filter(is_adult=False)
    
    if q:
        webtoons = webtoons.filter(
            Q(title__icontains=q)
            # | Q(writers__icontains=q)  # 필요하면 필드 추가
        )
    
    serializer = WebtoonSerializer(webtoons, many=True, context={'request': request})
    
    return Response({
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
    
    # 여기서 is_up=True 먼저 오게 정렬
    favorites = favorites.order_by('-is_up', 'title')
    
    serializer = WebtoonSerializer(favorites, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
