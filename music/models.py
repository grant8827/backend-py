from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Track(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    duration = models.FloatField()
    file_path = models.CharField(max_length=500, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracks')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tracks'

class Playlist(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    tracks = models.ManyToManyField(Track, through='PlaylistTrack')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'playlists'

class PlaylistTrack(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    position = models.IntegerField()
    
    class Meta:
        db_table = 'playlist_tracks'
        unique_together = ['playlist', 'position']