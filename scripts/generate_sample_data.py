# Gera dados de exemplo

import sys
import os
from datetime import datetime, timedelta
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_collector import DataCollector


def generate_sample_data(num_sessions: int = 10, duration_per_session: int = 30):
    collector = DataCollector("TOTEM-001")
    
    for i in range(num_sessions):
        print(f"Sessão {i+1}/{num_sessions}...")
        stats = collector.collect_and_store(duration_seconds=duration_per_session)
        print(f"  {stats['events_stored']} eventos")
    
    collector.db.close()
    print("Concluído!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Gera dados de exemplo')
    parser.add_argument('--sessions', type=int, default=10, help='Número de sessões a gerar')
    parser.add_argument('--duration', type=int, default=30, help='Duração de cada sessão em segundos')
    
    args = parser.parse_args()
    
    generate_sample_data(args.sessions, args.duration)

