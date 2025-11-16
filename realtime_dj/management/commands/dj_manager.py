"""
Real-time DJ Management Command
Django management command to handle real-time DJ session operations
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from realtime_dj.models import DJSession, DJTrackInstance, AudioLevelSnapshot
import json


class Command(BaseCommand):
    help = 'Manage real-time DJ sessions and track operations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['list', 'create', 'stop', 'cleanup'],
            help='Action to perform'
        )
        parser.add_argument('--session-name', type=str, help='Session name for creation')
        parser.add_argument('--dj-id', type=str, help='DJ user ID (UUID)')
        parser.add_argument('--session-id', type=str, help='Session ID for operations')
        parser.add_argument('--days', type=int, default=7, help='Days to keep for cleanup')
    
    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'list':
            self.list_sessions()
        elif action == 'create':
            self.create_session(options)
        elif action == 'stop':
            self.stop_session(options)
        elif action == 'cleanup':
            self.cleanup_old_data(options)
    
    def list_sessions(self):
        """List all active DJ sessions"""
        sessions = DJSession.objects.filter(ended_at__isnull=True).select_related()
        
        if not sessions:
            self.stdout.write(self.style.SUCCESS('No active sessions found.'))
            return
        
        self.stdout.write(self.style.SUCCESS('Active DJ Sessions:'))
        self.stdout.write('-' * 80)
        
        for session in sessions:
            status = "🔴 LIVE" if session.is_live else "⏸️  PAUSED"
            listeners = f"👥 {session.current_listeners}"
            duration = timezone.now() - session.started_at
            
            self.stdout.write(
                f"{status} {session.session_name} | "
                f"DJ: {session.dj_id} | "
                f"{listeners} | "
                f"Duration: {duration}"
            )
    
    def create_session(self, options):
        """Create a new DJ session"""
        session_name = options.get('session_name')
        dj_id = options.get('dj_id')
        
        if not session_name or not dj_id:
            self.stdout.write(
                self.style.ERROR('--session-name and --dj-id are required for creation')
            )
            return
        
        try:
            session = DJSession.objects.create(
                dj_id=dj_id,
                session_name=session_name,
                description=f"Auto-created session for {session_name}",
                is_live=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Created session "{session.session_name}" with ID: {session.id}'
                )
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error creating session: {e}'))
    
    def stop_session(self, options):
        """Stop a running DJ session"""
        session_id = options.get('session_id')
        
        if not session_id:
            self.stdout.write(self.style.ERROR('--session-id is required'))
            return
        
        try:
            session = DJSession.objects.get(id=session_id, ended_at__isnull=True)
            session.ended_at = timezone.now()
            session.is_live = False
            session.save()
            
            # End any active tracks
            DJTrackInstance.objects.filter(
                session=session,
                ended_at__isnull=True
            ).update(ended_at=timezone.now(), is_playing=False)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Session "{session.session_name}" stopped')
            )
            
        except DJSession.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Session not found or already ended'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error stopping session: {e}'))
    
    def cleanup_old_data(self, options):
        """Clean up old DJ session data"""
        days = options['days']
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        # Count records to be deleted
        old_sessions = DJSession.objects.filter(ended_at__lt=cutoff_date)
        old_snapshots = AudioLevelSnapshot.objects.filter(timestamp__lt=cutoff_date)
        
        session_count = old_sessions.count()
        snapshot_count = old_snapshots.count()
        
        if session_count == 0 and snapshot_count == 0:
            self.stdout.write(self.style.SUCCESS('No old data to clean up.'))
            return
        
        # Delete old data
        old_snapshots.delete()
        old_sessions.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🧹 Cleaned up {session_count} old sessions and '
                f'{snapshot_count} audio snapshots (older than {days} days)'
            )
        )