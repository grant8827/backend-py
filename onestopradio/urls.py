"""
OneStopRadio URL Configuration
API endpoints for authentication, station management, and streaming
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API v1 endpoints
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/stations/', include('stations.urls')),
    path('api/v1/streams/', include('streams.urls')),
    path('api/v1/social/', include('social_media.urls')),
    path('api/v1/music/', include('music.urls')),
    path('', include('realtime_dj.urls')),  # DJ real-time endpoints
    
    # Health check
    path('api/health/', include('onestopradio.health_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)