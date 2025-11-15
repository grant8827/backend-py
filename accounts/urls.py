"""
Authentication URLs
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    register_user,
    login_user,
    logout_user,
    UserProfileView,
    change_password,
)

urlpatterns = [
    # Authentication endpoints
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('change-password/', change_password, name='change_password'),
]