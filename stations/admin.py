"""
Station admin configuration
"""

from django.contrib import admin
from .models import Station, StationSettings


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'genre', 'is_public', 'total_listeners', 'created_at')
    list_filter = ('genre', 'is_public', 'allow_chat', 'created_at')
    search_fields = ('name', 'user__email', 'user__dj_name')
    readonly_fields = ('id', 'total_listeners', 'peak_listeners', 'total_hours', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description', 'genre')
        }),
        ('Media Assets', {
            'fields': ('logo', 'cover_image')
        }),
        ('Social Media', {
            'fields': ('youtube_url', 'twitch_url', 'facebook_url', 'instagram_url', 'twitter_url'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_public', 'allow_chat', 'auto_record', 'max_bitrate')
        }),
        ('Statistics', {
            'fields': ('total_listeners', 'peak_listeners', 'total_hours', 'last_stream'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StationSettings)
class StationSettingsAdmin(admin.ModelAdmin):
    list_display = ('station', 'audio_quality', 'enable_auto_dj', 'auto_archive')
    list_filter = ('audio_quality', 'enable_auto_dj', 'auto_archive')
    search_fields = ('station__name', 'station__user__email')