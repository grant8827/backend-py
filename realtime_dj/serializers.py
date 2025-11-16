"""
Real-time DJ Serializers
Django REST Framework serializers for DJ session API endpoints
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    DJSession, 
    DJTrackInstance, 
    AudioLevelSnapshot, 
    DJMixerState, 
    LiveStreamMetrics
)

User = get_user_model()


class DJSessionSerializer(serializers.ModelSerializer):
    """
    DJ Session serializer with full session information
    """
    dj_username = serializers.CharField(source='dj.username', read_only=True)
    station_name = serializers.CharField(source='station.name', read_only=True)
    duration = serializers.DurationField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = DJSession
        fields = [
            'id', 'dj', 'dj_username', 'station', 'station_name',
            'session_name', 'description', 'started_at', 'ended_at',
            'is_live', 'is_recording', 'sample_rate', 'bit_depth', 'channels',
            'current_listeners', 'peak_listeners',
            'master_level_left', 'master_level_right',
            'channel_a_level', 'channel_b_level',
            'crossfader_position', 'master_volume',
            'duration', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DJSessionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new DJ sessions
    """
    class Meta:
        model = DJSession
        fields = [
            'session_name', 'description', 'station',
            'sample_rate', 'bit_depth', 'channels'
        ]
    
    def create(self, validated_data):
        # Automatically set the DJ to the current user
        validated_data['dj'] = self.context['request'].user
        return super().create(validated_data)


class DJSessionUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating DJ session state (real-time updates)
    """
    class Meta:
        model = DJSession
        fields = [
            'is_live', 'is_recording', 'current_listeners',
            'master_level_left', 'master_level_right',
            'channel_a_level', 'channel_b_level',
            'crossfader_position', 'master_volume'
        ]


class DJTrackInstanceSerializer(serializers.ModelSerializer):
    """
    DJ Track Instance serializer with complete track information
    """
    track_title_display = serializers.CharField(source='track_title', read_only=True)
    current_bpm = serializers.FloatField(read_only=True)
    
    class Meta:
        model = DJTrackInstance
        fields = [
            'id', 'session', 'track', 'track_title', 'track_artist', 'track_duration',
            'deck', 'started_at', 'ended_at', 'current_position', 'playback_speed',
            'is_playing', 'is_looping', 'volume',
            'eq_low', 'eq_mid', 'eq_high',
            'detected_bpm', 'manual_bpm', 'current_bpm', 'is_synced',
            'cue_points', 'hot_cues', 'track_title_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DJTrackInstanceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for loading tracks onto DJ decks
    """
    class Meta:
        model = DJTrackInstance
        fields = [
            'session', 'track', 'track_title', 'track_artist', 'track_duration', 'deck'
        ]
    
    def validate(self, data):
        # Ensure only one active track per deck per session
        if DJTrackInstance.objects.filter(
            session=data['session'],
            deck=data['deck'],
            ended_at__isnull=True
        ).exists():
            raise serializers.ValidationError(
                f"Deck {data['deck']} already has an active track in this session"
            )
        return data


class DJTrackInstanceUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for real-time track control updates
    """
    class Meta:
        model = DJTrackInstance
        fields = [
            'current_position', 'playback_speed', 'is_playing', 'is_looping',
            'volume', 'eq_low', 'eq_mid', 'eq_high',
            'manual_bpm', 'is_synced', 'cue_points', 'hot_cues'
        ]


class AudioLevelSnapshotSerializer(serializers.ModelSerializer):
    """
    Audio Level Snapshot serializer for real-time level monitoring
    """
    class Meta:
        model = AudioLevelSnapshot
        fields = [
            'id', 'session', 'timestamp',
            'master_left', 'master_right', 'master_peak_left', 'master_peak_right',
            'channel_a_left', 'channel_a_right', 'channel_b_left', 'channel_b_right',
            'channel_a_peak', 'channel_b_peak', 'frequency_data'
        ]
        read_only_fields = ['id', 'timestamp']


class DJMixerStateSerializer(serializers.ModelSerializer):
    """
    DJ Mixer State serializer for mixer control updates
    """
    class Meta:
        model = DJMixerState
        fields = [
            'id', 'session', 'crossfader', 'master_volume',
            'channel_a_volume', 'channel_a_eq_low', 'channel_a_eq_mid', 
            'channel_a_eq_high', 'channel_a_filter',
            'channel_b_volume', 'channel_b_eq_low', 'channel_b_eq_mid', 
            'channel_b_eq_high', 'channel_b_filter',
            'bpm_master', 'sync_enabled', 'effects_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LiveStreamMetricsSerializer(serializers.ModelSerializer):
    """
    Live Stream Metrics serializer for streaming performance data
    """
    bitrate_kbps = serializers.SerializerMethodField()
    
    class Meta:
        model = LiveStreamMetrics
        fields = [
            'id', 'session', 'timestamp',
            'current_listeners', 'unique_listeners',
            'bitrate', 'bitrate_kbps', 'dropped_frames', 'buffer_health',
            'bandwidth_usage', 'latency', 'listener_locations'
        ]
        read_only_fields = ['id', 'timestamp']
    
    def get_bitrate_kbps(self, obj):
        return obj.bitrate / 1000 if obj.bitrate else 0


# Summary serializers for dashboard views
class DJSessionSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight DJ session serializer for list views
    """
    dj_username = serializers.CharField(source='dj.username', read_only=True)
    station_name = serializers.CharField(source='station.name', read_only=True)
    duration = serializers.DurationField(read_only=True)
    
    class Meta:
        model = DJSession
        fields = [
            'id', 'dj_username', 'station_name', 'session_name',
            'started_at', 'is_live', 'current_listeners',
            'duration'
        ]


class ActiveTrackSerializer(serializers.ModelSerializer):
    """
    Serializer for currently active tracks on decks
    """
    class Meta:
        model = DJTrackInstance
        fields = [
            'id', 'deck', 'track_title', 'track_artist',
            'current_position', 'track_duration', 'is_playing',
            'volume', 'current_bpm'
        ]


class RealtimeStatsSerializer(serializers.Serializer):
    """
    Combined real-time statistics for dashboard
    """
    session = DJSessionSummarySerializer(read_only=True)
    active_tracks = ActiveTrackSerializer(many=True, read_only=True)
    latest_audio_levels = AudioLevelSnapshotSerializer(read_only=True)
    current_mixer_state = DJMixerStateSerializer(read_only=True)
    latest_stream_metrics = LiveStreamMetricsSerializer(read_only=True)