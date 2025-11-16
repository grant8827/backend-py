"""
Django management command for PostgreSQL optimization and monitoring
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import time


class Command(BaseCommand):
    help = 'PostgreSQL optimization and monitoring tools for OneStopRadio'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['status', 'optimize', 'vacuum', 'analyze', 'reindex'],
            default='status',
            help='Action to perform: status, optimize, vacuum, analyze, or reindex'
        )
        parser.add_argument(
            '--table',
            type=str,
            help='Specific table to target (optional)'
        )

    def handle(self, *args, **options):
        action = options['action']
        table = options.get('table')
        
        self.stdout.write(self.style.SUCCESS(f'🔧 PostgreSQL {action.upper()} - OneStopRadio'))
        
        if action == 'status':
            self.show_status()
        elif action == 'optimize':
            self.optimize_database()
        elif action == 'vacuum':
            self.vacuum_database(table)
        elif action == 'analyze':
            self.analyze_database(table)
        elif action == 'reindex':
            self.reindex_database(table)

    def show_status(self):
        """Show comprehensive PostgreSQL status"""
        cursor = connection.cursor()
        
        # Basic database info
        cursor.execute("""
            SELECT 
                version(),
                current_database(),
                current_user,
                inet_server_addr(),
                inet_server_port(),
                pg_database_size(current_database()) as db_size
        """)
        db_info = cursor.fetchone()
        
        self.stdout.write('\n📊 Database Information:')
        self.stdout.write(f'  PostgreSQL Version: {db_info[0]}')
        self.stdout.write(f'  Database: {db_info[1]}')
        self.stdout.write(f'  User: {db_info[2]}')
        self.stdout.write(f'  Server: {db_info[3]}:{db_info[4]}')
        self.stdout.write(f'  Database Size: {self.format_bytes(db_info[5])}')
        
        # Connection info
        cursor.execute("""
            SELECT 
                count(*) as total_connections,
                count(*) filter (where state = 'active') as active_connections,
                count(*) filter (where state = 'idle') as idle_connections
            FROM pg_stat_activity 
            WHERE datname = current_database()
        """)
        conn_info = cursor.fetchone()
        
        self.stdout.write('\n🔗 Connection Status:')
        self.stdout.write(f'  Total Connections: {conn_info[0]}')
        self.stdout.write(f'  Active: {conn_info[1]}')
        self.stdout.write(f'  Idle: {conn_info[2]}')
        
        # Table statistics
        cursor.execute("""
            SELECT 
                schemaname,
                relname as tablename,
                n_tup_ins as inserts,
                n_tup_upd as updates,
                n_tup_del as deletes,
                n_live_tup as live_tuples,
                n_dead_tup as dead_tuples,
                last_vacuum,
                last_autovacuum,
                last_analyze,
                last_autoanalyze
            FROM pg_stat_user_tables
            ORDER BY n_live_tup DESC
            LIMIT 10
        """)
        
        tables = cursor.fetchall()
        if tables:
            self.stdout.write('\n📋 Top Tables by Size:')
            for table in tables:
                self.stdout.write(f'  {table[0]}.{table[1]}:')
                self.stdout.write(f'    Live tuples: {table[5]:,}')
                self.stdout.write(f'    Dead tuples: {table[6]:,}')
                self.stdout.write(f'    Last vacuum: {table[7] or "Never"}')
                self.stdout.write(f'    Last analyze: {table[9] or "Never"}')
        
        # Index usage
        cursor.execute("""
            SELECT 
                schemaname,
                relname as tablename,
                indexrelname as indexname,
                idx_tup_read,
                idx_tup_fetch,
                idx_scan
            FROM pg_stat_user_indexes
            WHERE idx_scan > 0
            ORDER BY idx_scan DESC
            LIMIT 10
        """)
        
        indexes = cursor.fetchall()
        if indexes:
            self.stdout.write('\n📈 Most Used Indexes:')
            for idx in indexes:
                self.stdout.write(f'  {idx[2]} ({idx[0]}.{idx[1]}): {idx[5]:,} scans')

        cursor.close()

    def optimize_database(self):
        """Run full database optimization"""
        self.stdout.write('\n🚀 Starting database optimization...')
        
        start_time = time.time()
        
        # Vacuum and analyze all tables
        self.vacuum_database()
        self.analyze_database()
        
        # Reindex if needed
        cursor = connection.cursor()
        cursor.execute("""
            SELECT schemaname, relname as tablename, n_dead_tup, n_live_tup
            FROM pg_stat_user_tables
            WHERE n_dead_tup > (n_live_tup * 0.1)  -- More than 10% dead tuples
            AND n_live_tup > 1000  -- Significant table size
        """)
        
        tables_needing_reindex = cursor.fetchall()
        if tables_needing_reindex:
            self.stdout.write(f'\n🔄 Reindexing {len(tables_needing_reindex)} tables with high dead tuple ratio...')
            for table_info in tables_needing_reindex:
                self.reindex_database(f'{table_info[0]}.{table_info[1]}')
        
        cursor.close()
        
        total_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Database optimization completed in {total_time:.2f} seconds')
        )

    def vacuum_database(self, table=None):
        """Vacuum database or specific table"""
        cursor = connection.cursor()
        
        if table:
            self.stdout.write(f'🧹 Vacuuming table: {table}')
            cursor.execute(f'VACUUM ANALYZE {table}')
        else:
            self.stdout.write('🧹 Vacuuming entire database...')
            cursor.execute('VACUUM ANALYZE')
        
        cursor.close()
        self.stdout.write(self.style.SUCCESS('✅ Vacuum completed'))

    def analyze_database(self, table=None):
        """Analyze database statistics"""
        cursor = connection.cursor()
        
        if table:
            self.stdout.write(f'📊 Analyzing table: {table}')
            cursor.execute(f'ANALYZE {table}')
        else:
            self.stdout.write('📊 Analyzing database statistics...')
            cursor.execute('ANALYZE')
        
        cursor.close()
        self.stdout.write(self.style.SUCCESS('✅ Analysis completed'))

    def reindex_database(self, table=None):
        """Reindex database or specific table"""
        cursor = connection.cursor()
        
        if table:
            self.stdout.write(f'🔄 Reindexing table: {table}')
            cursor.execute(f'REINDEX TABLE {table}')
        else:
            self.stdout.write('🔄 Reindexing entire database...')
            cursor.execute('REINDEX DATABASE railway')
        
        cursor.close()
        self.stdout.write(self.style.SUCCESS('✅ Reindexing completed'))

    def format_bytes(self, bytes_size):
        """Format bytes in human readable format"""
        if bytes_size is None:
            return "Unknown"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"