from django.urls import path
from .api_views import me_view, signup_view, login_view, logout_view

urlpatterns = [
    path('me/', me_view, name='api-me'),
    path('signup/', signup_view, name='api-signup'),
    path('login/', login_view, name='api-login'),
    path('logout/', logout_view, name='api-logout'),
]
