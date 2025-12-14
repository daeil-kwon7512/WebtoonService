from django.urls import path
from .api_views import (webtoon_list,
                        webtoon_detail,
                        toggle_favorite,
                        my_favorites,
                        recommend_by_favorites,
                        recommend_by_synopsis,
                        )
urlpatterns = [
    path('webtoons/', webtoon_list, name='api-webtoon-list'),
    path('webtoons/<int:webtoon_id>/', webtoon_detail, name='api-webtoon-detail'),
    path('webtoons/<int:webtoon_id>/favorite/', toggle_favorite, name='api-toggle-favorite'),
    path('me/favorites/', my_favorites, name='api-my-favorites'),
    # 추천 시스템 URL 추가
    path('webtoons/favorites/', recommend_by_favorites, name='api-recommend-favorites'),
    path('webtoons/synopsis/<int:webtoon_id>/', recommend_by_synopsis, name='api-recommend-synopsis'),
]
