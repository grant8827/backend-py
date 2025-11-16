"""
Real-time DJ WebSocket Routing
Django Channels routing for WebSocket connections
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/dj/sessions/(?P<session_id>[0-9a-f-]+)/$', consumers.DJSessionConsumer.as_asgi()),
    re_path(r'ws/dj/global/$', consumers.DJGlobalConsumer.as_asgi()),
]