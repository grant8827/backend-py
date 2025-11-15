"""
Radio Station models
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Station(models.Model):
    """Radio station model for DJ broadcasting"""
    
    GENRE_CHOICES = [
        ('electronic', 'Electronic'),
        ('rock', 'Rock'),
        ('pop', 'Pop'),
        ('jazz', 'Jazz'),
        ('classical', 'Classical'),
        ('hip_hop', 'Hip Hop'),
        ('r_and_b', 'R&B'),
        ('country', 'Country'),
        ('folk', 'Folk'),
        ('reggae', 'Reggae'),
        ('latin', 'Latin'),
        ('world', 'World'),
        ('talk', 'Talk'),
        ('news', 'News'),
        ('mixed', 'Mixed'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='station')
    
    # Basic information
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, max_length=500)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='mixed')
    
    # Media assets
    logo = models.ImageField(upload_to='station_logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='station_covers/', blank=True, null=True)
    
    # Social media links
    youtube_url = models.URLField(blank=True, null=True)
    twitch_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    
    # Station settings
    is_public = models.BooleanField(default=True)
    allow_chat = models.BooleanField(default=True)
    auto_record = models.BooleanField(default=False)
    max_bitrate = models.IntegerField(default=320, help_text="Maximum bitrate in kbps")
    
    # Statistics (updated by external services)
    total_listeners = models.IntegerField(default=0)
    peak_listeners = models.IntegerField(default=0)
    total_hours = models.FloatField(default=0.0, help_text="Total broadcast hours")
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_stream = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'stations'
        verbose_name = 'Station'
        verbose_name_plural = 'Stations'
    
    def __str__(self):
        return f"{self.name} ({self.user.display_name})"
    
    @property
    def social_links(self):
        """Return dictionary of social media links"""
        return {
            'youtube': self.youtube_url,
            'twitch': self.twitch_url,
            'facebook': self.facebook_url,
            'instagram': self.instagram_url,
            'twitter': self.twitter_url,
        }
    
    def update_stream_stats(self, listeners=None, duration_minutes=None):
        """Update station statistics from streaming session"""
        if listeners is not None:
            self.total_listeners = listeners
            if listeners > self.peak_listeners:
                self.peak_listeners = listeners
        
        if duration_minutes is not None:
            self.total_hours += duration_minutes / 60.0
        
        self.last_stream = timezone.now()
        self.save(update_fields=['total_listeners', 'peak_listeners', 'total_hours', 'last_stream'])


class StationSettings(models.Model):
    """Extended station settings and preferences"""
    
    station = models.OneToOneField(Station, on_delete=models.CASCADE, related_name='settings_extended')
    
    # Advanced audio settings
    audio_quality = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('high', 'High'), ('premium', 'Premium')],
        default='high'
    )
    enable_auto_dj = models.BooleanField(default=False)
    crossfade_duration = models.IntegerField(default=3, help_text="Crossfade duration in seconds")
    
    # Recording settings
    recording_format = models.CharField(
        max_length=10,
        choices=[('mp3', 'MP3'), ('aac', 'AAC'), ('flac', 'FLAC')],
        default='mp3'
    )
    auto_archive = models.BooleanField(default=True)
    archive_duration_days = models.IntegerField(default=30)
    
    # Notification settings
    notify_on_listeners = models.BooleanField(default=True)
    listener_threshold = models.IntegerField(default=10)
    notify_on_errors = models.BooleanField(default=True)
    
    # API keys and integrations (encrypted in production)
    last_fm_api_key = models.CharField(max_length=255, blank=True)
    spotify_client_id = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'station_settings'
        verbose_name = 'Station Settings'
        verbose_name_plural = 'Station Settings'