# Coletor de dados

import sys
import os
from datetime import datetime
from typing import List, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sensors.sensor_simulator import SensorSimulator
from src.database.db_connection import DatabaseManager


class DataCollector:
    def __init__(self, totem_id: str = "TOTEM-001"):
        self.simulator = SensorSimulator(totem_id)
        self.db = DatabaseManager()
        self.totem_id = totem_id
        self._ensure_totem_exists()
    
    def _ensure_totem_exists(self):
        try:
            query = "SELECT id FROM totems WHERE totem_id = %s"
            result = self.db.execute_query(query, (self.totem_id,))
            
            if not result:
                self.db.execute_insert('totems', {
                    'totem_id': self.totem_id,
                    'location': 'FIAP - Campus',
                    'status': 'active'
                })
        except Exception as e:
            print(f"Erro ao verificar totem: {e}")
    
    def collect_and_store(self, duration_seconds: int = 60) -> Dict:
        session_id = self.simulator.start_session()
        started_at = datetime.now().isoformat()
        self.db.create_session(session_id, self.totem_id, started_at)
        
        events = self.simulator.simulate_interaction_cycle(duration_seconds, fast_mode=True)
        
        stored_count = 0
        touch_events = []
        
        for event in events:
            if event.get('event_type') == 'session_end':
                continue
            
            try:
                self.db.insert_sensor_event(event)
                stored_count += 1
                
                if event.get('event_type') == 'touch' and event.get('value') == 1:
                    touch_events.append(event)
            except Exception as e:
                print(f"Erro ao armazenar evento: {e}")
        
        session_end = self.simulator.end_session()
        self.db.end_session(
            session_id,
            session_end['ended_at'],
            session_end['duration'],
            len(touch_events)
        )
        
        aggregates = self._calculate_aggregates(session_id, events, touch_events)
        self.db.insert_session_aggregate(aggregates)
        
        return {
            'session_id': session_id,
            'events_stored': stored_count,
            'touch_events': len(touch_events),
            'session_duration': session_end['duration']
        }
    
    def _calculate_aggregates(self, session_id: str, events: List[Dict], touch_events: List[Dict]) -> Dict:
        short_touches = sum(1 for e in touch_events if e.get('touch_type') == 'short')
        long_touches = sum(1 for e in touch_events if e.get('touch_type') == 'long')
        
        presence_events = [e for e in events if e.get('event_type') == 'presence' and e.get('value') == 1]
        avg_presence_time = len(presence_events)
        
        ldr_events = [e for e in events if e.get('event_type') == 'ldr']
        avg_light = sum(e.get('value', 0) for e in ldr_events) / len(ldr_events) if ldr_events else 0
        
        session_duration = sum(e.get('duration', 0) for e in touch_events) if touch_events else 0
        
        base_score = min(len(touch_events) * 10, 50)
        duration_score = min(session_duration * 5, 30)
        type_score = long_touches * 5
        interaction_score = min(base_score + duration_score + type_score, 100)
        
        return {
            'session_id': session_id,
            'totem_id': self.totem_id,
            'total_touches': len(touch_events),
            'short_touches': short_touches,
            'long_touches': long_touches,
            'avg_presence_time': round(avg_presence_time, 2),
            'avg_light_level': round(avg_light, 2),
            'session_duration': round(session_duration, 2),
            'interaction_score': round(interaction_score, 2)
        }


if __name__ == "__main__":
    collector = DataCollector("TOTEM-001")
    stats = collector.collect_and_store(duration_seconds=30)
    
    print(f"Sessão: {stats['session_id']}")
    print(f"Eventos: {stats['events_stored']}")
    print(f"Toques: {stats['touch_events']}")
    
    collector.db.close()

