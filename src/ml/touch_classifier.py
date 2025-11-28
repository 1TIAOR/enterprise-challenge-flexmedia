"""
Modelo de Machine Learning Supervisionado
Classifica tipo de interação (toque curto ou longo) baseado em features
"""

import sys
import os
import pandas as pd
import numpy as np
from typing import Dict
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database.db_connection import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TouchClassifier:
    """Classifica tipo de toque usando ML supervisionado"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.db = DatabaseManager()
    
    def prepare_training_data(self) -> pd.DataFrame:
        """
        Prepara dados de treinamento a partir do banco
        Extrai features relevantes para classificação
        """
        try:
            query = """
                SELECT 
                    se.duration,
                    se.touch_type,
                    se.value,
                    s.duration_seconds as session_duration,
                    sa.total_touches,
                    sa.avg_light_level,
                    EXTRACT(EPOCH FROM (se.timestamp - s.started_at)) as time_in_session
                FROM sensor_events se
                JOIN sessions s ON se.session_id = s.session_id
                LEFT JOIN session_aggregates sa ON s.session_id = sa.session_id
                WHERE se.event_type = 'touch'
                AND se.value = 1
                AND se.duration IS NOT NULL
                AND se.touch_type IN ('short', 'long')
            """
            
            results = self.db.execute_query(query)
            
            if not results:
                logger.warning("Nenhum dado de treinamento encontrado. Gerando dados sintéticos...")
                return self._generate_synthetic_data()
            
            df = pd.DataFrame(results)
            
            # Remove valores nulos
            df = df.dropna()
            
            # Garante que temos dados suficientes
            if len(df) < 20:
                logger.warning("Poucos dados reais. Complementando com dados sintéticos...")
                synthetic = self._generate_synthetic_data()
                df = pd.concat([df, synthetic], ignore_index=True)
            
            return df
        except Exception as e:
            logger.error(f"Erro ao preparar dados: {e}")
            return self._generate_synthetic_data()
    
    def _generate_synthetic_data(self, n_samples: int = 100) -> pd.DataFrame:
        """Gera dados sintéticos para treinamento quando não há dados suficientes"""
        np.random.seed(42)
        
        data = []
        
        for _ in range(n_samples):
            # Toques curtos: duração 0.1-1.0s
            if np.random.random() < 0.5:
                duration = np.random.uniform(0.1, 1.0)
                touch_type = 'short'
            else:
                # Toques longos: duração 1.0-2.0s
                duration = np.random.uniform(1.0, 2.0)
                touch_type = 'long'
            
            data.append({
                'duration': duration,
                'touch_type': touch_type,
                'value': 1,
                'session_duration': np.random.uniform(10, 120),
                'total_touches': np.random.randint(1, 10),
                'avg_light_level': np.random.uniform(300, 800),
                'time_in_session': np.random.uniform(0, 60)
            })
        
        return pd.DataFrame(data)
    
    def extract_features(self, df: pd.DataFrame) -> tuple:
        """Extrai features e target do DataFrame"""
        # Features
        feature_cols = ['duration', 'session_duration', 'total_touches', 
                       'avg_light_level', 'time_in_session']
        
        X = df[feature_cols].copy()
        
        # Target (classificação binária: short=0, long=1)
        y = (df['touch_type'] == 'long').astype(int)
        
        return X, y
    
    def train(self, test_size: float = 0.2, random_state: int = 42):
        """Treina o modelo de classificação"""
        logger.info("Preparando dados de treinamento...")
        
        df = self.prepare_training_data()
        
        if df.empty:
            raise ValueError("Não há dados suficientes para treinamento")
        
        logger.info(f"Dataset preparado: {len(df)} amostras")
        
        # Extrai features
        X, y = self.extract_features(df)
        
        # Divide em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Normaliza features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Treina modelo (Random Forest)
        logger.info("Treinando modelo Random Forest...")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=random_state,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Avalia modelo
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Acurácia do modelo: {accuracy:.2%}")
        logger.info("\nRelatório de Classificação:")
        logger.info(classification_report(y_test, y_pred, target_names=['short', 'long']))
        
        return {
            'accuracy': accuracy,
            'train_size': len(X_train),
            'test_size': len(X_test),
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
    
    def predict(self, duration: float, session_duration: float = None, 
                total_touches: int = None, avg_light: float = None,
                time_in_session: float = None) -> Dict:
        """Prediz tipo de toque baseado em features"""
        if self.model is None:
            raise ValueError("Modelo não foi treinado. Execute train() primeiro.")
        
        # Valores padrão se não fornecidos
        session_duration = session_duration or 60.0
        total_touches = total_touches or 1
        avg_light = avg_light or 512.0
        time_in_session = time_in_session or 0.0
        
        # Prepara features
        features = np.array([[duration, session_duration, total_touches, 
                            avg_light, time_in_session]])
        
        # Normaliza
        features_scaled = self.scaler.transform(features)
        
        # Prediz
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        
        return {
            'predicted_type': 'long' if prediction == 1 else 'short',
            'probability_short': round(probabilities[0], 3),
            'probability_long': round(probabilities[1], 3),
            'confidence': round(max(probabilities), 3)
        }
    
    def save_model(self, filepath: str = 'models/touch_classifier.pkl'):
        """Salva modelo treinado"""
        if self.model is None:
            raise ValueError("Modelo não foi treinado")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, filepath)
        
        logger.info(f"Modelo salvo em {filepath}")
    
    def load_model(self, filepath: str = 'models/touch_classifier.pkl'):
        """Carrega modelo salvo"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Modelo não encontrado: {filepath}")
        
        loaded = joblib.load(filepath)
        self.model = loaded['model']
        self.scaler = loaded['scaler']
        
        logger.info(f"Modelo carregado de {filepath}")


if __name__ == "__main__":
    classifier = TouchClassifier()
    
    print("=== Treinamento do Modelo de Classificação ===\n")
    
    # Treina modelo
    results = classifier.train()
    
    print(f"\nAcurácia: {results['accuracy']:.2%}")
    print(f"Dados de treino: {results['train_size']}")
    print(f"Dados de teste: {results['test_size']}")
    
    # Testa predição
    print("\n=== Teste de Predição ===")
    test_cases = [
        {'duration': 0.5, 'session_duration': 30, 'total_touches': 3},
        {'duration': 1.5, 'session_duration': 60, 'total_touches': 5},
        {'duration': 0.8, 'session_duration': 45, 'total_touches': 2}
    ]
    
    for case in test_cases:
        prediction = classifier.predict(**case)
        print(f"\nDuração: {case['duration']}s")
        print(f"Predição: {prediction['predicted_type']}")
        print(f"Confiança: {prediction['confidence']:.1%}")
    
    # Salva modelo
    classifier.save_model('src/ml/models/touch_classifier.pkl')
    
    classifier.db.close()

