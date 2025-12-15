from django.urls import path
from .api_views import webtoon_list, webtoon_detail, toggle_favorite, my_favorites, survey_candidates_view

urlpatterns = [
    path('webtoons/', webtoon_list, name='api-webtoon-list'),
    path('webtoons/<int:webtoon_id>/', webtoon_detail, name='api-webtoon-detail'),
    path('webtoons/<int:webtoon_id>/favorite/', toggle_favorite, name='api-toggle-favorite'),
    path('me/favorites/', my_favorites, name='api-my-favorites'),
    path('survey/candidates/', survey_candidates_view, name='survey-candidates'), # 설문조사 조회용
]
