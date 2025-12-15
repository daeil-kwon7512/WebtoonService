from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from .api_views import me_view, signup_view, survey_submit_view


urlpatterns = [
    # 커스텀 뷰 연결
    path('me/', me_view, name='api-me'),    # 내정보 조회
    path('signup/', signup_view, name='api-signup'),    # 회원가입
    
    # SimpleJWT 제공 뷰 연결
    # 로그인 (ID/PW -> Access/Refresh Token 발급)
    path('login/', TokenObtainPairView.as_view(), name='api-login'),
    # 토큰 갱신 (Refresh -> Access 발급)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 로그아웃 (Refresh Token 차단)
    path('logout/', TokenBlacklistView.as_view(), name='api-logout'),
    
    # 설문조사 결과 제출
    path('survey/submit/', survey_submit_view, name='api-survey-submit'), # 추가됨
]
