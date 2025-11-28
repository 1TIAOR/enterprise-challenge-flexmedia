# Conexão com banco de dados

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import os
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gerencia conexões e operações no banco de dados"""
    
    def __init__(self, 
                 host: str = None,
                 port: int = None,
                 database: str = None,
                 user: str = None,
                 password: str = None):
        """
        Inicializa conexão com banco de dados
        Usa variáveis de ambiente se não fornecidas
        """
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = port or int(os.getenv('DB_PORT', 5432))
        self.database = database or os.getenv('DB_NAME', 'flexmedia_totem')
        self.user = user or os.getenv('DB_USER', 'postgres')
        self.password = password or os.getenv('DB_PASSWORD', 'postgres')
        
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Estabelece conexão com o banco"""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
        except psycopg2.Error as e:
            print(f"Erro ao conectar: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Erro na query: {e}")
            raise
    
    def execute_insert(self, table: str, data: Dict) -> int:
        try:
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ', '.join(['%s'] * len(values))
            
            query = f"""
                INSERT INTO {table} ({', '.join(columns)})
                VALUES ({placeholders})
                RETURNING id
            """
            
            with self.conn.cursor() as cursor:
                cursor.execute(query, values)
                inserted_id = cursor.fetchone()[0]
                self.conn.commit()
                return inserted_id
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Erro ao inserir: {e}")
            raise
    
    def insert_sensor_event(self, event: Dict) -> int:
        data = {
            'session_id': event.get('session_id'),
            'totem_id': event.get('totem_id'),
            'event_type': event.get('event_type'),
            'value': event.get('value'),
            'duration': event.get('duration'),
            'touch_type': event.get('touch_type'),
            'timestamp': event.get('timestamp')
        }
        return self.execute_insert('sensor_events', data)
    
    def create_session(self, session_id: str, totem_id: str, started_at: str) -> int:
        data = {
            'session_id': session_id,
            'totem_id': totem_id,
            'started_at': started_at
        }
        return self.execute_insert('sessions', data)
    
    def end_session(self, session_id: str, ended_at: str, duration: float, total_interactions: int):
        try:
            query = """
                UPDATE sessions
                SET ended_at = %s,
                    duration_seconds = %s,
                    total_interactions = %s
                WHERE session_id = %s
            """
            with self.conn.cursor() as cursor:
                cursor.execute(query, (ended_at, duration, total_interactions, session_id))
                self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Erro ao finalizar sessão: {e}")
            raise
    
    def insert_session_aggregate(self, aggregate: Dict) -> int:
        return self.execute_insert('session_aggregates', aggregate)
    
    def get_totem_stats(self, totem_id: str = None) -> List[Dict]:
        if totem_id:
            query = """
                SELECT 
                    COUNT(DISTINCT s.session_id) as total_sessions,
                    SUM(sa.total_touches) as total_touches,
                    AVG(sa.interaction_score) as avg_interaction_score,
                    AVG(s.duration_seconds) as avg_session_duration
                FROM sessions s
                LEFT JOIN session_aggregates sa ON s.session_id = sa.session_id
                WHERE s.totem_id = %s
            """
            return self.execute_query(query, (totem_id,))
        else:
            query = """
                SELECT 
                    t.totem_id,
                    COUNT(DISTINCT s.session_id) as total_sessions,
                    SUM(sa.total_touches) as total_touches,
                    AVG(sa.interaction_score) as avg_interaction_score
                FROM totems t
                LEFT JOIN sessions s ON t.totem_id = s.totem_id
                LEFT JOIN session_aggregates sa ON s.session_id = sa.session_id
                GROUP BY t.totem_id
            """
            return self.execute_query(query)
    
    def close(self):
        """Fecha conexão com o banco"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

