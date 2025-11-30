from django.urls import path
from .api_views import webtoon_list, webtoon_detail, toggle_favorite, my_favorites

urlpatterns = [
    path('webtoons/', webtoon_list, name='api-webtoon-list'),
    path('webtoons/<int:webtoon_id>/', webtoon_detail, name='api-webtoon-detail'),
    path('webtoons/<int:webtoon_id>/favorite/', toggle_favorite, name='api-toggle-favorite'),
    path('me/favorites/', my_favorites, name='api-my-favorites'),
]
