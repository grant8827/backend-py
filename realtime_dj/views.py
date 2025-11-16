"""
Real-time DJ Views
Django REST Framework views for DJ session management and real-time updates
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Prefetch
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

from .models import (
    DJSession, 
    DJTrackInstance, 
    AudioLevelSnapshot, 
    DJMixerState, 
    LiveStreamMetrics
)
from .serializers import (
    DJSessionSerializer,
    DJSessionCreateSerializer,
    DJSessionUpdateSerializer,
    DJTrackInstanceSerializer,
    DJTrackInstanceCreateSerializer,
    DJTrackInstanceUpdateSerializer,
    AudioLevelSnapshotSerializer,
    DJMixerStateSerializer,
    LiveStreamMetricsSerializer,
    RealtimeStatsSerializer,
    ActiveTrackSerializer
)


class DJSessionViewSet(viewsets.ModelViewSet):
    """
    DJ Session management viewset
    Handles CRUD operations for DJ sessions with real-time capabilities
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return DJSession.objects.filter(dj=user).select_related('dj', 'station')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DJSessionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DJSessionUpdateSerializer
        return DJSessionSerializer
    
    def perform_create(self, serializer):
        """Create a new DJ session"""
        session = serializer.save(dj=self.request.user)
        
        # Send WebSocket notification
        self._broadcast_session_event('session_created', session)
    
    def perform_update(self, serializer):
        """Update DJ session with real-time broadcasting"""
        session = serializer.save()
        
        # Broadcast real-time updates
        self._broadcast_session_update(session)
    
    @action(detail=True, methods=['post'])
    def start_session(self, request, pk=None):
        """Start a DJ session (go live)"""
        session = self.get_object()
        
        if session.is_live:
            return Response(
                {'error': 'Session is already live'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.is_live = True
        session.started_at = timezone.now()
        session.save()
        
        self._broadcast_session_event('session_started', session)
        
        return Response({
            'message': 'Session started',
            'session': DJSessionSerializer(session).data
        })
    
    @action(detail=True, methods=['post'])
    def end_session(self, request, pk=None):
        """End a DJ session (go offline)"""
        session = self.get_object()
        
        if not session.is_live:
            return Response(
                {'error': 'Session is not currently live'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.is_live = False
        session.ended_at = timezone.now()
        session.save()
        
        # Also end any active tracks
        DJTrackInstance.objects.filter(
            session=session,
            ended_at__isnull=True
        ).update(ended_at=timezone.now(), is_playing=False)
        
        self._broadcast_session_event('session_ended', session)
        
        return Response({
            'message': 'Session ended',
            'session': DJSessionSerializer(session).data
        })
    
    @action(detail=True, methods=['get'])
    def realtime_stats(self, request, pk=None):
        """Get comprehensive real-time statistics for a session"""
        session = self.get_object()
        
        # Get active tracks
        active_tracks = DJTrackInstance.objects.filter(
            session=session,
            ended_at__isnull=True
        ).order_by('deck')
        
        # Get latest audio levels
        latest_audio_levels = AudioLevelSnapshot.objects.filter(
            session=session
        ).order_by('-timestamp').first()
        
        # Get current mixer state
        current_mixer_state = DJMixerState.objects.filter(
            session=session
        ).order_by('-updated_at').first()
        
        # Get latest stream metrics
        latest_stream_metrics = LiveStreamMetrics.objects.filter(
            session=session
        ).order_by('-timestamp').first()
        
        stats_data = {
            'session': session,
            'active_tracks': active_tracks,
            'latest_audio_levels': latest_audio_levels,
            'current_mixer_state': current_mixer_state,
            'latest_stream_metrics': latest_stream_metrics
        }
        
        serializer = RealtimeStatsSerializer(stats_data)
        return Response(serializer.data)
    
    def _broadcast_session_event(self, event_type, session):
        """Broadcast session events via WebSocket"""
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"dj_session_{session.id}",
                {
                    'type': 'session_event',
                    'event': event_type,
                    'session_id': str(session.id),
                    'data': DJSessionSerializer(session).data
                }
            )
    
    def _broadcast_session_update(self, session):
        """Broadcast real-time session updates"""
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"dj_session_{session.id}",
                {
                    'type': 'session_update',
                    'session_id': str(session.id),
                    'data': DJSessionUpdateSerializer(session).data
                }
            )


class DJTrackInstanceViewSet(viewsets.ModelViewSet):
    """
    DJ Track Instance management viewset
    Handles track loading and real-time playback control
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        session_id = self.request.query_params.get('session_id')
        queryset = DJTrackInstance.objects.select_related('session', 'track')
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        # Only show tracks from user's sessions
        return queryset.filter(session__dj=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DJTrackInstanceCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DJTrackInstanceUpdateSerializer
        return DJTrackInstanceSerializer
    
    def perform_update(self, serializer):
        """Update track with real-time broadcasting"""
        track_instance = serializer.save()
        
        # Broadcast real-time updates
        self._broadcast_track_update(track_instance)
    
    @action(detail=True, methods=['post'])
    def play(self, request, pk=None):
        """Start playing a track"""
        track_instance = self.get_object()
        track_instance.is_playing = True
        track_instance.save()
        
        self._broadcast_track_event('track_play', track_instance)
        
        return Response({
            'message': 'Track playing',
            'track': DJTrackInstanceSerializer(track_instance).data
        })
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause a track"""
        track_instance = self.get_object()
        track_instance.is_playing = False
        track_instance.save()
        
        self._broadcast_track_event('track_pause', track_instance)
        
        return Response({
            'message': 'Track paused',
            'track': DJTrackInstanceSerializer(track_instance).data
        })
    
    @action(detail=True, methods=['post'])
    def seek(self, request, pk=None):
        """Seek to a specific position in the track"""
        track_instance = self.get_object()
        position = request.data.get('position', 0)
        
        track_instance.current_position = float(position)
        track_instance.save()
        
        self._broadcast_track_event('track_seek', track_instance)
        
        return Response({
            'message': f'Seek to {position}s',
            'track': DJTrackInstanceSerializer(track_instance).data
        })
    
    @action(detail=True, methods=['post'])
    def add_cue(self, request, pk=None):
        """Add a cue point to the track"""
        track_instance = self.get_object()
        cue_name = request.data.get('name', f'Cue {len(track_instance.cue_points) + 1}')
        position = request.data.get('position', track_instance.current_position)
        
        cue_points = track_instance.cue_points.copy()
        cue_points[cue_name] = position
        track_instance.cue_points = cue_points
        track_instance.save()
        
        self._broadcast_track_event('cue_added', track_instance)
        
        return Response({
            'message': f'Cue point "{cue_name}" added at {position}s',
            'track': DJTrackInstanceSerializer(track_instance).data
        })
    
    def _broadcast_track_event(self, event_type, track_instance):
        """Broadcast track events via WebSocket"""
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"dj_session_{track_instance.session.id}",
                {
                    'type': 'track_event',
                    'event': event_type,
                    'track_id': str(track_instance.id),
                    'deck': track_instance.deck,
                    'data': DJTrackInstanceSerializer(track_instance).data
                }
            )
    
    def _broadcast_track_update(self, track_instance):
        """Broadcast real-time track updates"""
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"dj_session_{track_instance.session.id}",
                {
                    'type': 'track_update',
                    'track_id': str(track_instance.id),
                    'deck': track_instance.deck,
                    'data': DJTrackInstanceUpdateSerializer(track_instance).data
                }
            )


class AudioLevelSnapshotViewSet(viewsets.ModelViewSet):
    """
    Audio Level Snapshot viewset
    Handles real-time audio level reporting
    """
    serializer_class = AudioLevelSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post']  # Only allow GET and POST methods
    
    def get_queryset(self):
        session_id = self.request.query_params.get('session_id')
        queryset = AudioLevelSnapshot.objects.select_related('session').order_by('-timestamp')
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        return queryset.filter(session__dj=self.request.user)
    
    def perform_create(self, serializer):
        """Create audio level snapshot and broadcast"""
        snapshot = serializer.save()
        
        # Update session with latest levels
        session = snapshot.session
        session.master_level_left = snapshot.master_left
        session.master_level_right = snapshot.master_right
        session.channel_a_level = max(snapshot.channel_a_left, snapshot.channel_a_right)
        session.channel_b_level = max(snapshot.channel_b_left, snapshot.channel_b_right)
        session.save(update_fields=[
            'master_level_left', 'master_level_right', 
            'channel_a_level', 'channel_b_level'
        ])
        
        # Broadcast real-time levels
        self._broadcast_audio_levels(snapshot)
    
    def _broadcast_audio_levels(self, snapshot):
        """Broadcast audio levels via WebSocket"""
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"dj_session_{snapshot.session.id}",
                {
                    'type': 'audio_levels',
                    'data': AudioLevelSnapshotSerializer(snapshot).data
                }
            )


class DJMixerStateViewSet(viewsets.ModelViewSet):
    """
    DJ Mixer State viewset
    Handles mixer configuration and EQ settings
    """
    serializer_class = DJMixerStateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        session_id = self.request.query_params.get('session_id')
        queryset = DJMixerState.objects.select_related('session')
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        return queryset.filter(session__dj=self.request.user)
    
    def perform_create(self, serializer):
        """Create mixer state and broadcast"""
        mixer_state = serializer.save()
        self._broadcast_mixer_update(mixer_state)
    
    def perform_update(self, serializer):
        """Update mixer state and broadcast"""
        mixer_state = serializer.save()
        self._broadcast_mixer_update(mixer_state)
    
    def _broadcast_mixer_update(self, mixer_state):
        """Broadcast mixer updates via WebSocket"""
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"dj_session_{mixer_state.session.id}",
                {
                    'type': 'mixer_update',
                    'data': DJMixerStateSerializer(mixer_state).data
                }
            )


class LiveStreamMetricsViewSet(viewsets.ModelViewSet):
    """
    Live Stream Metrics viewset
    Handles streaming performance data collection
    """
    serializer_class = LiveStreamMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post']  # Only allow GET and POST methods
    
    def get_queryset(self):
        session_id = self.request.query_params.get('session_id')
        queryset = LiveStreamMetrics.objects.select_related('session').order_by('-timestamp')
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        return queryset.filter(session__dj=self.request.user)
    
    def perform_create(self, serializer):
        """Create stream metrics and broadcast"""
        metrics = serializer.save()
        
        # Update session listener count
        session = metrics.session
        session.current_listeners = metrics.current_listeners
        if metrics.current_listeners > session.peak_listeners:
            session.peak_listeners = metrics.current_listeners
        session.save(update_fields=['current_listeners', 'peak_listeners'])
        
        # Broadcast metrics update
        self._broadcast_stream_metrics(metrics)
    
    def _broadcast_stream_metrics(self, metrics):
        """Broadcast stream metrics via WebSocket"""
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"dj_session_{metrics.session.id}",
                {
                    'type': 'stream_metrics',
                    'data': LiveStreamMetricsSerializer(metrics).data
                }
            )
