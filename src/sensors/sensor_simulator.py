# Simulador de sensores

import random
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List
import uuid


class SensorSimulator:
    
    def __init__(self, totem_id: str = "TOTEM-001"):
        self.totem_id = totem_id
        self.session_id = None
        self.session_start = None
        self.is_active = False
        
    def generate_touch_event(self) -> Dict:
        # 30% de chance de toque
        touch_detected = 1 if random.random() < 0.3 else 0
        
        if touch_detected:
            touch_duration = random.uniform(0.1, 2.0)
            touch_type = "long" if touch_duration > 1.0 else "short"
        else:
            touch_duration = 0.0
            touch_type = "none"
        
        return {
            "event_type": "touch",
            "timestamp": datetime.now().isoformat(),
            "value": touch_detected,
            "duration": round(touch_duration, 2),
            "touch_type": touch_type,
            "totem_id": self.totem_id,
            "session_id": self.session_id
        }
    
    def generate_presence_event(self) -> Dict:
        # 60% de chance de presença
        presence_detected = 1 if random.random() < 0.6 else 0
        
        return {
            "event_type": "presence",
            "timestamp": datetime.now().isoformat(),
            "value": presence_detected,
            "totem_id": self.totem_id,
            "session_id": self.session_id
        }
    
    def generate_ldr_event(self) -> Dict:
        hour = datetime.now().hour
        if 8 <= hour <= 18:
            light_value = random.randint(600, 1023)
        else:
            light_value = random.randint(100, 400)
        
        return {
            "event_type": "ldr",
            "timestamp": datetime.now().isoformat(),
            "value": light_value,
            "totem_id": self.totem_id,
            "session_id": self.session_id
        }
    
    def start_session(self) -> str:
        self.session_id = str(uuid.uuid4())
        self.session_start = datetime.now()
        self.is_active = True
        return self.session_id
    
    def end_session(self):
        self.is_active = False
        session_duration = None
        if self.session_start:
            session_duration = (datetime.now() - self.session_start).total_seconds()
        
        return {
            "session_id": self.session_id,
            "duration": round(session_duration, 2) if session_duration else 0,
            "ended_at": datetime.now().isoformat()
        }
    
    def generate_all_sensors(self) -> List[Dict]:
        events = []
        
        presence = self.generate_presence_event()
        events.append(presence)
        
        if presence["value"] == 1:
            touch = self.generate_touch_event()
            events.append(touch)
        
        ldr = self.generate_ldr_event()
        events.append(ldr)
        
        return events
    
    def simulate_interaction_cycle(self, duration_seconds: int = 60, fast_mode: bool = True) -> List[Dict]:
        all_events = []
        
        if not self.is_active or self.session_id is None:
            self.start_session()
        
        if fast_mode:
            base_time = self.session_start if self.session_start else datetime.now()
            
            for second in range(duration_seconds):
                event_time = base_time.replace(microsecond=0) + timedelta(seconds=second)
                events = self.generate_all_sensors()
                
                for event in events:
                    event['timestamp'] = event_time.isoformat()
                
                all_events.extend(events)
        else:
            start_time = time.time()
            while time.time() - start_time < duration_seconds:
                events = self.generate_all_sensors()
                all_events.extend(events)
                time.sleep(1)
        
        session_end = self.end_session()
        all_events.append({
            "event_type": "session_end",
            **session_end
        })
        
        return all_events


if __name__ == "__main__":
    simulator = SensorSimulator("TOTEM-001")
    
    for i in range(10):
        events = simulator.generate_all_sensors()
        for event in events:
            print(json.dumps(event, indent=2, ensure_ascii=False))
        print("-" * 50)
        time.sleep(0.5)

