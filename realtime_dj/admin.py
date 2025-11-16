"""
Real-time DJ Admin Interface
Django admin configuration for DJ session management
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    DJSession, 
    DJTrackInstance, 
    AudioLevelSnapshot, 
    DJMixerState, 
    LiveStreamMetrics
)


@admin.register(DJSession)
class DJSessionAdmin(admin.ModelAdmin):
    list_display = [
        'session_name', 'dj', 'is_live', 'is_recording', 
        'current_listeners', 'started_at', 'duration_display'
    ]
    list_filter = ['is_live', 'is_recording', 'started_at', 'station']
    search_fields = ['session_name', 'dj__username', 'dj__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'duration_display']
    
    fieldsets = (
        ('Session Info', {
            'fields': ('id', 'session_name', 'description', 'dj', 'station')
        }),
        ('Timing', {
            'fields': ('started_at', 'ended_at', 'duration_display')
        }),
        ('Status', {
            'fields': ('is_live', 'is_recording')
        }),
        ('Audio Configuration', {
            'fields': ('sample_rate', 'bit_depth', 'channels')
        }),
        ('Live Statistics', {
            'fields': ('current_listeners', 'peak_listeners')
        }),
        ('Audio Levels', {
            'fields': (
                'master_level_left', 'master_level_right',
                'channel_a_level', 'channel_b_level'
            )
        }),
        ('Mixer Controls', {
            'fields': ('crossfader_position', 'master_volume')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def duration_display(self, obj):
        duration = obj.duration
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return format_html(
            '<span style="font-family: monospace;">{:02.0f}:{:02.0f}:{:02.0f}</span>',
            hours, minutes, seconds
        )
    duration_display.short_description = 'Duration'


class DJTrackInstanceInline(admin.TabularInline):
    model = DJTrackInstance
    extra = 0
    readonly_fields = ['id', 'started_at', 'created_at']
    fields = [
        'deck', 'track_title', 'track_artist', 'is_playing', 
        'current_position', 'volume', 'started_at'
    ]


@admin.register(DJTrackInstance)
class DJTrackInstanceAdmin(admin.ModelAdmin):
    list_display = [
        'track_title', 'track_artist', 'deck', 'session', 
        'is_playing', 'current_position_display', 'started_at'
    ]
    list_filter = ['deck', 'is_playing', 'is_synced', 'started_at']
    search_fields = ['track_title', 'track_artist', 'session__session_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Track Info', {
            'fields': ('id', 'session', 'track', 'track_title', 'track_artist', 'track_duration')
        }),
        ('Deck Assignment', {
            'fields': ('deck', 'started_at', 'ended_at')
        }),
        ('Playback Controls', {
            'fields': ('is_playing', 'current_position', 'playback_speed', 'is_looping')
        }),
        ('DJ Controls', {
            'fields': ('volume', 'eq_low', 'eq_mid', 'eq_high')
        }),
        ('BPM & Sync', {
            'fields': ('detected_bpm', 'manual_bpm', 'is_synced')
        }),
        ('Cue Points', {
            'fields': ('cue_points', 'hot_cues'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def current_position_display(self, obj):
        if obj.track_duration:
            progress = (obj.current_position / obj.track_duration) * 100
            return format_html(
                '<span style="font-family: monospace;">{:.1f}s ({:.1f}%)</span>',
                obj.current_position, progress
            )
        return format_html('<span style="font-family: monospace;">{:.1f}s</span>', obj.current_position)
    current_position_display.short_description = 'Position'


@admin.register(AudioLevelSnapshot)
class AudioLevelSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        'session', 'timestamp', 'master_peak_display', 
        'channel_a_peak_display', 'channel_b_peak_display'
    ]
    list_filter = ['timestamp', 'session']
    readonly_fields = ['id', 'timestamp']
    
    fieldsets = (
        ('Session', {
            'fields': ('id', 'session', 'timestamp')
        }),
        ('Master Levels', {
            'fields': ('master_left', 'master_right', 'master_peak_left', 'master_peak_right')
        }),
        ('Channel A', {
            'fields': ('channel_a_left', 'channel_a_right', 'channel_a_peak')
        }),
        ('Channel B', {
            'fields': ('channel_b_left', 'channel_b_right', 'channel_b_peak')
        }),
        ('Frequency Data', {
            'fields': ('frequency_data',),
            'classes': ('collapse',)
        })
    )
    
    def master_peak_display(self, obj):
        peak = max(obj.master_peak_left, obj.master_peak_right)
        color = 'red' if peak > 0.9 else 'orange' if peak > 0.7 else 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}</span>',
            color, peak
        )
    master_peak_display.short_description = 'Master Peak'
    
    def channel_a_peak_display(self, obj):
        color = 'red' if obj.channel_a_peak > 0.9 else 'orange' if obj.channel_a_peak > 0.7 else 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}</span>',
            color, obj.channel_a_peak
        )
    channel_a_peak_display.short_description = 'Ch A Peak'
    
    def channel_b_peak_display(self, obj):
        color = 'red' if obj.channel_b_peak > 0.9 else 'orange' if obj.channel_b_peak > 0.7 else 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}</span>',
            color, obj.channel_b_peak
        )
    channel_b_peak_display.short_description = 'Ch B Peak'


@admin.register(DJMixerState)
class DJMixerStateAdmin(admin.ModelAdmin):
    list_display = [
        'session', 'crossfader_display', 'master_volume_display',
        'bpm_master', 'sync_enabled', 'updated_at'
    ]
    list_filter = ['sync_enabled', 'updated_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Session', {
            'fields': ('id', 'session')
        }),
        ('Master Controls', {
            'fields': ('crossfader', 'master_volume')
        }),
        ('Channel A', {
            'fields': (
                'channel_a_volume', 'channel_a_eq_low', 
                'channel_a_eq_mid', 'channel_a_eq_high', 'channel_a_filter'
            )
        }),
        ('Channel B', {
            'fields': (
                'channel_b_volume', 'channel_b_eq_low', 
                'channel_b_eq_mid', 'channel_b_eq_high', 'channel_b_filter'
            )
        }),
        ('BPM & Sync', {
            'fields': ('bpm_master', 'sync_enabled')
        }),
        ('Effects', {
            'fields': ('effects_active',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def crossfader_display(self, obj):
        position = obj.crossfader
        if position < -0.3:
            return format_html('<span style="color: blue;">← A ({:.2f})</span>', position)
        elif position > 0.3:
            return format_html('<span style="color: red;">B → ({:.2f})</span>', position)
        else:
            return format_html('<span style="color: green;">Center ({:.2f})</span>', position)
    crossfader_display.short_description = 'Crossfader'
    
    def master_volume_display(self, obj):
        volume = obj.master_volume
        color = 'red' if volume > 0.9 else 'orange' if volume > 0.7 else 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}</span>',
            color, volume
        )
    master_volume_display.short_description = 'Master Vol'


@admin.register(LiveStreamMetrics)
class LiveStreamMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'session', 'timestamp', 'current_listeners', 'bitrate_display',
        'buffer_health_display', 'latency_display'
    ]
    list_filter = ['timestamp', 'session']
    readonly_fields = ['id', 'timestamp']
    
    fieldsets = (
        ('Session', {
            'fields': ('id', 'session', 'timestamp')
        }),
        ('Listeners', {
            'fields': ('current_listeners', 'unique_listeners')
        }),
        ('Quality Metrics', {
            'fields': ('bitrate', 'dropped_frames', 'buffer_health')
        }),
        ('Network', {
            'fields': ('bandwidth_usage', 'latency')
        }),
        ('Geographic Data', {
            'fields': ('listener_locations',),
            'classes': ('collapse',)
        })
    )
    
    def bitrate_display(self, obj):
        bitrate_kbps = obj.bitrate / 1000
        color = 'green' if bitrate_kbps >= 128 else 'orange' if bitrate_kbps >= 64 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.0f} kbps</span>',
            color, bitrate_kbps
        )
    bitrate_display.short_description = 'Bitrate'
    
    def buffer_health_display(self, obj):
        health = obj.buffer_health
        color = 'green' if health >= 0.8 else 'orange' if health >= 0.5 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1%}</span>',
            color, health
        )
    buffer_health_display.short_description = 'Buffer Health'
    
    def latency_display(self, obj):
        if obj.latency is None:
            return '-'
        color = 'green' if obj.latency < 100 else 'orange' if obj.latency < 500 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.0f} ms</span>',
            color, obj.latency
        )
    latency_display.short_description = 'Latency'


# Add inline for DJSession admin
DJSessionAdmin.inlines = [DJTrackInstanceInline]
