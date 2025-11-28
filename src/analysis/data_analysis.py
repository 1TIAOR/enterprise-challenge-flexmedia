# Análise de dados

import sys
import os
from typing import Dict, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database.db_connection import DatabaseManager


class DataAnalyzer:
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def load_data_to_dataframe(self, totem_id: str = None, days: int = 30) -> pd.DataFrame:
        try:
            date_filter = datetime.now() - timedelta(days=days)
            
            if totem_id:
                query = """
                    SELECT 
                        se.*,
                        s.started_at as session_started,
                        s.duration_seconds as session_duration
                    FROM sensor_events se
                    JOIN sessions s ON se.session_id = s.session_id
                    WHERE se.totem_id = %s
                    AND se.timestamp >= %s
                    ORDER BY se.timestamp
                """
                params = (totem_id, date_filter)
            else:
                query = """
                    SELECT 
                        se.*,
                        s.started_at as session_started,
                        s.duration_seconds as session_duration
                    FROM sensor_events se
                    JOIN sessions s ON se.session_id = s.session_id
                    WHERE se.timestamp >= %s
                    ORDER BY se.timestamp
                """
                params = (date_filter,)
            
            results = self.db.execute_query(query, params)
            
            if not results:
                return pd.DataFrame()
            
            # Converte para DataFrame
            df = pd.DataFrame(results)
            
            # Converte timestamps
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            if 'session_started' in df.columns:
                df['session_started'] = pd.to_datetime(df['session_started'])
            
            return df
        except Exception as e:
            print(f"Erro: {e}")
            return pd.DataFrame()
    
    def get_descriptive_stats(self, df: pd.DataFrame) -> Dict:
        """Calcula estatísticas descritivas"""
        if df.empty:
            return {}
        
        stats = {}
        
        # Estatísticas por tipo de evento
        for event_type in df['event_type'].unique():
            type_df = df[df['event_type'] == event_type]
            
            if event_type in ['touch', 'presence']:
                # Para eventos binários
                stats[event_type] = {
                    'total_events': len(type_df),
                    'active_count': int(type_df['value'].sum()),
                    'inactive_count': int((type_df['value'] == 0).sum()),
                    'activation_rate': round(type_df['value'].mean() * 100, 2)
                }
            elif event_type == 'ldr':
                # Para LDR (valores contínuos)
                stats[event_type] = {
                    'total_events': len(type_df),
                    'mean': round(type_df['value'].mean(), 2),
                    'median': round(type_df['value'].median(), 2),
                    'std': round(type_df['value'].std(), 2),
                    'min': int(type_df['value'].min()),
                    'max': int(type_df['value'].max()),
                    'q25': round(type_df['value'].quantile(0.25), 2),
                    'q75': round(type_df['value'].quantile(0.75), 2)
                }
        
        # Estatísticas de sessões
        if 'session_duration' in df.columns:
            sessions_df = df.groupby('session_id').first()
            stats['sessions'] = {
                'total_sessions': len(sessions_df),
                'avg_duration': round(sessions_df['session_duration'].mean(), 2) if 'session_duration' in sessions_df.columns else 0,
                'total_duration': round(sessions_df['session_duration'].sum(), 2) if 'session_duration' in sessions_df.columns else 0
            }
        
        return stats
    
    def analyze_touch_patterns(self, df: pd.DataFrame) -> Dict:
        """Analisa padrões de toque"""
        touch_df = df[df['event_type'] == 'touch'].copy()
        
        if touch_df.empty:
            return {}
        
        # Filtra apenas toques ativos
        active_touches = touch_df[touch_df['value'] == 1]
        
        if active_touches.empty:
            return {'total_touches': 0}
        
        # Análise por tipo de toque
        touch_types = active_touches['touch_type'].value_counts().to_dict()
        
        # Análise de duração
        durations = active_touches['duration'].dropna()
        
        return {
            'total_touches': len(active_touches),
            'touch_types': touch_types,
            'avg_duration': round(durations.mean(), 2) if not durations.empty else 0,
            'median_duration': round(durations.median(), 2) if not durations.empty else 0,
            'max_duration': round(durations.max(), 2) if not durations.empty else 0,
            'min_duration': round(durations.min(), 2) if not durations.empty else 0
        }
    
    def analyze_temporal_patterns(self, df: pd.DataFrame) -> Dict:
        """Analisa padrões temporais (horário do dia, dia da semana)"""
        if df.empty or 'timestamp' not in df.columns:
            return {}
        
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()
        
        # Padrão por hora
        hourly = df.groupby('hour').size().to_dict()
        
        # Padrão por dia da semana
        daily = df.groupby('day_of_week').size().to_dict()
        
        # Hora de pico
        peak_hour = max(hourly.items(), key=lambda x: x[1])[0] if hourly else None
        
        return {
            'hourly_distribution': hourly,
            'daily_distribution': daily,
            'peak_hour': peak_hour,
            'peak_hour_count': hourly.get(peak_hour, 0) if peak_hour else 0
        }
    
    def calculate_engagement_metrics(self, df: pd.DataFrame) -> Dict:
        """Calcula métricas de engajamento"""
        if df.empty:
            return {}
        
        # Agrupa por sessão
        sessions = df.groupby('session_id')
        
        engagement_data = []
        
        for session_id, session_df in sessions:
            touches = session_df[session_df['event_type'] == 'touch']
            active_touches = touches[touches['value'] == 1]
            
            presence = session_df[session_df['event_type'] == 'presence']
            active_presence = presence[presence['value'] == 1]
            
            engagement_data.append({
                'session_id': session_id,
                'touch_count': len(active_touches),
                'presence_time': len(active_presence),
                'avg_light': session_df[session_df['event_type'] == 'ldr']['value'].mean() if 'ldr' in session_df['event_type'].values else 0
            })
        
        if not engagement_data:
            return {}
        
        engagement_df = pd.DataFrame(engagement_data)
        
        return {
            'avg_touches_per_session': round(engagement_df['touch_count'].mean(), 2),
            'avg_presence_time': round(engagement_df['presence_time'].mean(), 2),
            'high_engagement_sessions': int((engagement_df['touch_count'] >= 5).sum()),
            'low_engagement_sessions': int((engagement_df['touch_count'] < 2).sum()),
            'engagement_rate': round((engagement_df['touch_count'] > 0).mean() * 100, 2)
        }
    
    def generate_full_report(self, totem_id: str = None) -> Dict:
        """Gera relatório completo de análise"""
        
        df = self.load_data_to_dataframe(totem_id)
        
        if df.empty:
            return {'error': 'Nenhum dado encontrado'}
        
        report = {
            'descriptive_stats': self.get_descriptive_stats(df),
            'touch_patterns': self.analyze_touch_patterns(df),
            'temporal_patterns': self.analyze_temporal_patterns(df),
            'engagement_metrics': self.calculate_engagement_metrics(df),
            'data_period': {
                'start': df['timestamp'].min().isoformat() if 'timestamp' in df.columns else None,
                'end': df['timestamp'].max().isoformat() if 'timestamp' in df.columns else None,
                'total_records': len(df)
            }
        }
        
        return report


if __name__ == "__main__":
    analyzer = DataAnalyzer()
    
    print("=== Análise de Dados ===\n")
    
    # Gera relatório completo
    report = analyzer.generate_full_report()
    
    print("Estatísticas Descritivas:")
    print(report.get('descriptive_stats', {}))
    
    print("\nPadrões de Toque:")
    print(report.get('touch_patterns', {}))
    
    print("\nMétricas de Engajamento:")
    print(report.get('engagement_metrics', {}))
    
    analyzer.db.close()

