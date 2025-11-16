"""
Real-time DJ WebSocket Consumers
Django Channels WebSocket consumers for real-time DJ updates
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import DJSession

User = get_user_model()


class DJSessionConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time DJ session updates
    Handles connections to specific DJ sessions for live updates
    """
    
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'dj_session_{self.session_id}'
        
        # Join session group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial session data
        session_data = await self.get_session_data()
        if session_data:
            await self.send(text_data=json.dumps({
                'type': 'session_connected',
                'session': session_data
            }))
    
    async def disconnect(self, close_code):
        # Leave session group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json['type']
            
            if message_type == 'audio_levels':
                await self.handle_audio_levels(text_data_json)
            elif message_type == 'mixer_update':
                await self.handle_mixer_update(text_data_json)
            elif message_type == 'track_control':
                await self.handle_track_control(text_data_json)
            elif message_type == 'listener_update':
                await self.handle_listener_update(text_data_json)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    async def handle_audio_levels(self, data):
        """Handle real-time audio level updates"""
        levels = data.get('levels', {})
        
        # Broadcast to all clients in the session
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'audio_levels_update',
                'levels': levels
            }
        )
    
    async def handle_mixer_update(self, data):
        """Handle mixer control updates"""
        mixer_data = data.get('mixer', {})
        
        # Broadcast to all clients in the session
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'mixer_state_update',
                'mixer': mixer_data
            }
        )
    
    async def handle_track_control(self, data):
        """Handle track playback control updates"""
        track_data = data.get('track', {})
        
        # Broadcast to all clients in the session
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'track_control_update',
                'track': track_data
            }
        )
    
    async def handle_listener_update(self, data):
        """Handle listener count updates"""
        listener_count = data.get('listeners', 0)
        
        # Update session listener count in database
        await self.update_session_listeners(listener_count)
        
        # Broadcast to all clients in the session
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'listener_count_update',
                'listeners': listener_count
            }
        )
    
    # WebSocket message handlers
    async def session_event(self, event):
        """Send session event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'session_event',
            'event': event['event'],
            'data': event['data']
        }))
    
    async def session_update(self, event):
        """Send session update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'session_update',
            'data': event['data']
        }))
    
    async def track_event(self, event):
        """Send track event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'track_event',
            'event': event['event'],
            'deck': event['deck'],
            'data': event['data']
        }))
    
    async def track_update(self, event):
        """Send track update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'track_update',
            'deck': event['deck'],
            'data': event['data']
        }))
    
    async def audio_levels_update(self, event):
        """Send audio levels to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'audio_levels',
            'levels': event['levels']
        }))
    
    async def mixer_state_update(self, event):
        """Send mixer state to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'mixer_update',
            'mixer': event['mixer']
        }))
    
    async def track_control_update(self, event):
        """Send track control update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'track_control',
            'track': event['track']
        }))
    
    async def listener_count_update(self, event):
        """Send listener count update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'listener_count',
            'listeners': event['listeners']
        }))
    
    async def stream_metrics(self, event):
        """Send stream metrics to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'stream_metrics',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_session_data(self):
        """Get current session data from database"""
        try:
            session = DJSession.objects.get(id=self.session_id)
            return {
                'id': str(session.id),
                'session_name': session.session_name,
                'is_live': session.is_live,
                'current_listeners': session.current_listeners,
                'started_at': session.started_at.isoformat(),
                'master_volume': session.master_volume,
                'crossfader_position': session.crossfader_position
            }
        except DJSession.DoesNotExist:
            return None
    
    @database_sync_to_async
    def update_session_listeners(self, listener_count):
        """Update session listener count in database"""
        try:
            session = DJSession.objects.get(id=self.session_id)
            session.current_listeners = listener_count
            if listener_count > session.peak_listeners:
                session.peak_listeners = listener_count
            session.save(update_fields=['current_listeners', 'peak_listeners'])
        except DJSession.DoesNotExist:
            pass


class DJGlobalConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for global DJ platform updates
    Handles connections for platform-wide notifications
    """
    
    async def connect(self):
        self.room_group_name = 'dj_global_updates'
        
        # Join global updates group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send active sessions count
        active_sessions = await self.get_active_sessions_count()
        await self.send(text_data=json.dumps({
            'type': 'platform_stats',
            'active_sessions': active_sessions
        }))
    
    async def disconnect(self, close_code):
        # Leave global updates group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # WebSocket message handlers
    async def platform_notification(self, event):
        """Send platform notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'level': event.get('level', 'info')
        }))
    
    async def session_created(self, event):
        """Send new session notification"""
        await self.send(text_data=json.dumps({
            'type': 'session_created',
            'session': event['session_data']
        }))
    
    async def session_ended(self, event):
        """Send session ended notification"""
        await self.send(text_data=json.dumps({
            'type': 'session_ended',
            'session_id': event['session_id']
        }))
    
    @database_sync_to_async
    def get_active_sessions_count(self):
        """Get count of active DJ sessions"""
        return DJSession.objects.filter(ended_at__isnull=True).count()