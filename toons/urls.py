from django.urls import path
from . import views

app_name = "toons"
urlpatterns = [
    # 사용자가 http://localhost:8000/webtoon/ (프로젝트 레벨에서 'webtoon/'으로 연결했다고 가정)
    # 또는 http://localhost:8000/ 에 접속하면 views.py의 webtoon_list_view 함수가 실행됩니다.
    path('', views.webtoon_list, name='webtoon_list'),
    # 만약 플랫폼별 주소도 만들고 싶다면:
    # path('<str:platform>/', views.webtoon_platform_view, name='platform_list'),
    path('webtoons/<int:webtoon_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('mypage/', views.my_page, name='my_page'),
]