from django.urls import path
from . import views

urlpatterns = [
    path('tracks/', views.TrackListCreateView.as_view(), name='track-list-create'),
    path('playlists/', views.PlaylistListCreateView.as_view(), name='playlist-list-create'),
    path('upload/', views.upload_track, name='upload-track'),
]