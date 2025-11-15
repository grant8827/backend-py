"""
Station serializers for API responses
"""

from rest_framework import serializers
from .models import Station, StationSettings


class StationSerializer(serializers.ModelSerializer):
    """Serializer for Station model matching TypeScript interface"""
    
    social_links = serializers.ReadOnlyField()
    
    class Meta:
        model = Station
        fields = [
            'id', 'name', 'description', 'genre', 'logo', 'cover_image',
            'social_links', 'is_public', 'allow_chat', 'auto_record', 'max_bitrate',
            'total_listeners', 'peak_listeners', 'total_hours', 
            'created_at', 'updated_at', 'last_stream'
        ]
        read_only_fields = ['id', 'total_listeners', 'peak_listeners', 'total_hours', 
                           'created_at', 'updated_at', 'last_stream']


class StationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating stations"""
    
    class Meta:
        model = Station
        fields = ['name', 'description', 'genre', 'is_public', 'allow_chat', 'auto_record', 'max_bitrate']


class StationSocialLinksSerializer(serializers.ModelSerializer):
    """Serializer for updating social media links"""
    
    class Meta:
        model = Station
        fields = ['youtube_url', 'twitch_url', 'facebook_url', 'instagram_url', 'twitter_url']