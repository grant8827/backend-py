from rest_framework import serializers
from .models import Track, Playlist, PlaylistTrack

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['id', 'title', 'artist', 'duration', 'file_path', 'created_at']

class PlaylistTrackSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    
    class Meta:
        model = PlaylistTrack
        fields = ['track', 'position']

class PlaylistSerializer(serializers.ModelSerializer):
    tracks = PlaylistTrackSerializer(source='playlisttrack_set', many=True, read_only=True)
    
    class Meta:
        model = Playlist
        fields = ['id', 'name', 'tracks', 'created_at']