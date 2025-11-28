# Limpeza de dados

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.db_connection import DatabaseManager


class DataCleaner:
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def remove_duplicates(self) -> int:
        """
        Remove eventos duplicados baseado em session_id, event_type e timestamp
        Mantém apenas o primeiro registro
        """
        try:
            query = """
                DELETE FROM sensor_events
                WHERE id IN (
                    SELECT id
                    FROM (
                        SELECT id,
                               ROW_NUMBER() OVER (
                                   PARTITION BY session_id, event_type, timestamp 
                                   ORDER BY id
                               ) as rn
                        FROM sensor_events
                    ) t
                    WHERE t.rn > 1
                )
            """
            
            with self.db.conn.cursor() as cursor:
                cursor.execute(query)
                deleted_count = cursor.rowcount
                self.db.conn.commit()
                
            return deleted_count
        except Exception as e:
            self.db.conn.rollback()
            print(f"Erro: {e}")
            return 0
    
    def validate_sensor_values(self) -> Tuple[int, List[Dict]]:
        """
        Valida valores dos sensores
        - Touch/Presence: deve ser 0 ou 1
        - LDR: deve estar entre 0 e 1023
        Retorna número de registros inválidos e lista de erros
        """
        errors = []
        
        try:
            # Valida eventos de toque e presença
            query_touch = """
                SELECT id, event_type, value, timestamp
                FROM sensor_events
                WHERE event_type IN ('touch', 'presence')
                AND value NOT IN (0, 1)
            """
            invalid_touch = self.db.execute_query(query_touch)
            
            for record in invalid_touch:
                errors.append({
                    'id': record['id'],
                    'type': 'invalid_value',
                    'message': f"Evento {record['event_type']} com valor inválido: {record['value']}"
                })
            
            # Valida eventos LDR
            query_ldr = """
                SELECT id, event_type, value, timestamp
                FROM sensor_events
                WHERE event_type = 'ldr'
                AND (value < 0 OR value > 1023)
            """
            invalid_ldr = self.db.execute_query(query_ldr)
            
            for record in invalid_ldr:
                errors.append({
                    'id': record['id'],
                    'type': 'invalid_ldr',
                    'message': f"LDR com valor fora do range (0-1023): {record['value']}"
                })
            
            # Corrige valores inválidos
            if errors:
                self._fix_invalid_values(errors)
            
            return len(errors), errors
            
        except Exception as e:
            print(f"Erro: {e}")
            return 0, []
    
    def _fix_invalid_values(self, errors: List[Dict]):
        """Corrige valores inválidos"""
        try:
            for error in errors:
                record_id = error['id']
                
                if error['type'] == 'invalid_value':
                    # Corrige para 0 (inativo)
                    query = "UPDATE sensor_events SET value = 0 WHERE id = %s"
                elif error['type'] == 'invalid_ldr':
                    # Corrige para valor médio (512)
                    query = "UPDATE sensor_events SET value = 512 WHERE id = %s"
                else:
                    continue
                
                with self.db.conn.cursor() as cursor:
                    cursor.execute(query, (record_id,))
            
            self.db.conn.commit()
        except Exception as e:
            self.db.conn.rollback()
            print(f"Erro: {e}")
    
    def standardize_timestamps(self):
        """Padroniza timestamps para UTC"""
        try:
            query = """
                UPDATE sensor_events
                SET timestamp = timestamp AT TIME ZONE 'UTC'
                WHERE timestamp IS NOT NULL
            """
            
            with self.db.conn.cursor() as cursor:
                cursor.execute(query)
                updated_count = cursor.rowcount
                self.db.conn.commit()
            
            return updated_count
        except Exception as e:
            self.db.conn.rollback()
            print(f"Erro: {e}")
            return 0
    
    def remove_old_data(self, days: int = 90):
        """Remove dados antigos (padrão: 90 dias)"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Remove eventos antigos
            query_events = "DELETE FROM sensor_events WHERE timestamp < %s"
            with self.db.conn.cursor() as cursor:
                cursor.execute(query_events, (cutoff_date,))
                deleted_events = cursor.rowcount
            
            # Remove sessões antigas sem eventos
            query_sessions = """
                DELETE FROM sessions
                WHERE started_at < %s
                AND id NOT IN (
                    SELECT DISTINCT session_id::text::int
                    FROM sensor_events
                )
            """
            with self.db.conn.cursor() as cursor:
                cursor.execute(query_sessions, (cutoff_date,))
                deleted_sessions = cursor.rowcount
            
            self.db.conn.commit()
            
            return deleted_events + deleted_sessions
        except Exception as e:
            self.db.conn.rollback()
            print(f"Erro: {e}")
            return 0
    
    def clean_all(self):
        duplicates_removed = self.remove_duplicates()
        invalid_count, errors = self.validate_sensor_values()
        timestamps_standardized = self.standardize_timestamps()
        
        return {
            'duplicates_removed': duplicates_removed,
            'invalid_records_fixed': invalid_count,
            'timestamps_standardized': timestamps_standardized
        }
    
    def get_data_quality_report(self) -> Dict:
        """Gera relatório de qualidade dos dados"""
        try:
            # Total de registros
            total_query = "SELECT COUNT(*) as total FROM sensor_events"
            total = self.db.execute_query(total_query)[0]['total']
            
            # Registros por tipo
            type_query = """
                SELECT event_type, COUNT(*) as count
                FROM sensor_events
                GROUP BY event_type
            """
            by_type = self.db.execute_query(type_query)
            
            # Sessões completas
            sessions_query = """
                SELECT COUNT(*) as total
                FROM sessions
                WHERE ended_at IS NOT NULL
            """
            complete_sessions = self.db.execute_query(sessions_query)[0]['total']
            
            # Registros com problemas
            problems_query = """
                SELECT COUNT(*) as count
                FROM sensor_events
                WHERE (event_type IN ('touch', 'presence') AND value NOT IN (0, 1))
                   OR (event_type = 'ldr' AND (value < 0 OR value > 1023))
            """
            problems = self.db.execute_query(problems_query)[0]['count']
            
            return {
                'total_records': total,
                'records_by_type': {r['event_type']: r['count'] for r in by_type},
                'complete_sessions': complete_sessions,
                'records_with_problems': problems,
                'quality_score': round((1 - problems / total) * 100, 2) if total > 0 else 100
            }
        except Exception as e:
            print(f"Erro: {e}")
            return {}


if __name__ == "__main__":
    cleaner = DataCleaner()
    
    print("=== Limpeza de Dados ===\n")
    
    # Executa limpeza
    results = cleaner.clean_all()
    
    print(f"Duplicados removidos: {results['duplicates_removed']}")
    print(f"Registros inválidos corrigidos: {results['invalid_records_fixed']}")
    print(f"Timestamps padronizados: {results['timestamps_standardized']}")
    
    # Gera relatório
    print("\n=== Relatório de Qualidade ===")
    report = cleaner.get_data_quality_report()
    print(f"Total de registros: {report.get('total_records', 0)}")
    print(f"Registros por tipo: {report.get('records_by_type', {})}")
    print(f"Sessões completas: {report.get('complete_sessions', 0)}")
    print(f"Score de qualidade: {report.get('quality_score', 0)}%")
    
    cleaner.db.close()

