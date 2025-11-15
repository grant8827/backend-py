"""
Station management URLs
"""

from django.urls import path
from .views import StationDetailView, update_social_links, upload_logo, upload_cover

urlpatterns = [
    # Station management
    path('me/', StationDetailView.as_view(), name='station_detail'),
    path('me/social/', update_social_links, name='station_social_links'),
    path('me/logo/', upload_logo, name='station_logo_upload'),
    path('me/cover/', upload_cover, name='station_cover_upload'),
]