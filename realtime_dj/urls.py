"""
Real-time DJ URL Configuration
API routes for DJ session management and real-time updates
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'sessions', views.DJSessionViewSet, basename='djsession')
router.register(r'tracks', views.DJTrackInstanceViewSet, basename='djtrack')
router.register(r'audio-levels', views.AudioLevelSnapshotViewSet, basename='audiolevels')
router.register(r'mixer-state', views.DJMixerStateViewSet, basename='mixerstate')
router.register(r'stream-metrics', views.LiveStreamMetricsViewSet, basename='streammetrics')

app_name = 'realtime_dj'

urlpatterns = [
    path('api/v1/dj/', include(router.urls)),
]