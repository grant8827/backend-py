"""
Real-time DJ Player Models
Django models for live DJ sessions, track management, and audio processing
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import json

User = get_user_model()


class DJSession(models.Model):
    """
    Main DJ session model for live DJ performances
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dj = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dj_sessions', 
                          db_column='dj_id', to_field='id')
    station = models.ForeignKey('stations.Station', on_delete=models.CASCADE, 
                               related_name='dj_sessions', null=True, blank=True,
                               db_column='station_id', to_field='id')
    
    # Session metadata
    session_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Timing
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Session state
    is_live = models.BooleanField(default=False)
    is_recording = models.BooleanField(default=False)
    
    # Audio configuration
    sample_rate = models.PositiveIntegerField(default=48000)
    bit_depth = models.PositiveIntegerField(default=16, 
                                          validators=[MinValueValidator(8), MaxValueValidator(32)])
    channels = models.PositiveIntegerField(default=2,
                                         validators=[MinValueValidator(1), MaxValueValidator(8)])
    
    # Real-time statistics
    current_listeners = models.PositiveIntegerField(default=0)
    peak_listeners = models.PositiveIntegerField(default=0)
    
    # Audio levels (updated in real-time)
    master_level_left = models.FloatField(default=0.0,
                                        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    master_level_right = models.FloatField(default=0.0,
                                         validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    channel_a_level = models.FloatField(default=0.0,
                                       validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    channel_b_level = models.FloatField(default=0.0,
                                       validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # Mixer state
    crossfader_position = models.FloatField(default=0.0,
                                          validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)])
    master_volume = models.FloatField(default=0.8,
                                    validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'realtime_dj_djsession'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.session_name} - {self.dj.username}"
    
    @property
    def duration(self):
        """Calculate session duration"""
        end_time = self.ended_at or timezone.now()
        return end_time - self.started_at
    
    @property
    def is_active(self):
        """Check if session is currently active"""
        return self.ended_at is None


class DJTrackInstance(models.Model):
    """
    Individual track loaded onto a DJ deck during a session
    """
    DECK_CHOICES = [
        ('A', 'Deck A'),
        ('B', 'Deck B'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(DJSession, on_delete=models.CASCADE, related_name='track_instances',
                               db_column='session_id', to_field='id')
    
    # Track information  
    track = models.ForeignKey('music.Track', on_delete=models.SET_NULL, 
                             null=True, blank=True, related_name='dj_instances',
                             db_column='track_id', to_field='id')
    track_title = models.CharField(max_length=255)
    track_artist = models.CharField(max_length=255)
    track_duration = models.FloatField(null=True, blank=True)  # Duration in seconds
    
    # Deck assignment
    deck = models.CharField(max_length=1, choices=DECK_CHOICES)
    
    # Timing
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Playback state
    current_position = models.FloatField(default=0.0)  # Current position in seconds
    playback_speed = models.FloatField(default=1.0,    # Playback speed multiplier
                                     validators=[MinValueValidator(0.1), MaxValueValidator(3.0)])
    is_playing = models.BooleanField(default=False)
    is_looping = models.BooleanField(default=False)
    
    # DJ controls
    volume = models.FloatField(default=0.8,
                             validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    eq_low = models.FloatField(default=0.0,
                             validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)])
    eq_mid = models.FloatField(default=0.0,
                             validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)])
    eq_high = models.FloatField(default=0.0,
                              validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)])
    
    # BPM and sync
    detected_bpm = models.FloatField(null=True, blank=True,
                                   validators=[MinValueValidator(60.0), MaxValueValidator(200.0)])
    manual_bpm = models.FloatField(null=True, blank=True,
                                 validators=[MinValueValidator(60.0), MaxValueValidator(200.0)])
    is_synced = models.BooleanField(default=False)
    
    # Cue points (stored as JSON)
    cue_points = models.JSONField(default=dict, blank=True)
    hot_cues = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'realtime_dj_djtrackinstance'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.track_title} - Deck {self.deck} ({self.session.session_name})"
    
    @property
    def current_bpm(self):
        """Get the effective BPM (manual override or detected)"""
        return self.manual_bpm or self.detected_bpm


class AudioLevelSnapshot(models.Model):
    """
    Real-time audio level measurements
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(DJSession, on_delete=models.CASCADE, related_name='audio_snapshots',
                               db_column='session_id', to_field='id')
    
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Master levels
    master_left = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    master_right = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    master_peak_left = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    master_peak_right = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # Channel levels
    channel_a_left = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    channel_a_right = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    channel_b_left = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    channel_b_right = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # Peak levels for channels
    channel_a_peak = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    channel_b_peak = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # Optional frequency analysis data
    frequency_data = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'realtime_dj_audiolevelsnapshot'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Audio Levels - {self.session.session_name} ({self.timestamp})"


class DJMixerState(models.Model):
    """
    Current mixer configuration and EQ settings
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(DJSession, on_delete=models.CASCADE, related_name='mixer_states',
                               db_column='session_id', to_field='id')
    
    # Master controls
    crossfader = models.FloatField(default=0.0,
                                 validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)])
    master_volume = models.FloatField(default=0.8,
                                    validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # Channel A controls
    channel_a_volume = models.FloatField(default=0.8,
                                       validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    channel_a_eq_low = models.FloatField(default=0.0,
                                       validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)])
    channel_a_eq_mid = models.FloatField(default=0.0,
                                       validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)])
    channel_a_eq_high = models.FloatField(default=0.0,
                                        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)])
    channel_a_filter = models.FloatField(default=0.0,
                                       validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)])
    
    # Channel B controls
    channel_b_volume = models.FloatField(default=0.8,
                                       validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    channel_b_eq_low = models.FloatField(default=0.0,
                                       validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)])
    channel_b_eq_mid = models.FloatField(default=0.0,
                                       validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)])
    channel_b_eq_high = models.FloatField(default=0.0,
                                        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)])
    channel_b_filter = models.FloatField(default=0.0,
                                       validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)])
    
    # BPM and sync
    bpm_master = models.FloatField(null=True, blank=True,
                                 validators=[MinValueValidator(60.0), MaxValueValidator(200.0)])
    sync_enabled = models.BooleanField(default=False)
    
    # Effects (stored as JSON)
    effects_active = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'realtime_dj_djmixerstate'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Mixer State - {self.session.session_name} ({self.updated_at})"


class LiveStreamMetrics(models.Model):
    """
    Real-time streaming performance metrics
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(DJSession, on_delete=models.CASCADE, related_name='stream_metrics',
                               db_column='session_id', to_field='id')
    
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Listener statistics
    current_listeners = models.PositiveIntegerField(default=0)
    unique_listeners = models.PositiveIntegerField(default=0)
    
    # Streaming quality
    bitrate = models.PositiveIntegerField()  # bits per second
    dropped_frames = models.PositiveIntegerField(default=0)
    buffer_health = models.FloatField(default=1.0,
                                    validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # Network metrics
    bandwidth_usage = models.PositiveBigIntegerField()  # bytes per second
    latency = models.FloatField(null=True, blank=True)  # milliseconds
    
    # Geographic data (stored as JSON)
    listener_locations = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'realtime_dj_livestreammetrics'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Stream Metrics - {self.session.session_name} ({self.current_listeners} listeners)"
