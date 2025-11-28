# Diagrama de Fluxo de Dados - Sprint 2

## Fluxo Completo do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    SIMULADOR DE SENSORES                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                       │
│  │  Toque   │  │ Presença  │  │   LDR    │                       │
│  │ (0 ou 1) │  │ (0 ou 1)  │  │ (0-1023) │                       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                       │
│       │             │             │                              │
│       └─────────────┴─────────────┘                              │
│                    │                                              │
│              Eventos JSON                                         │
└────────────────────┼──────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COLETOR DE DADOS                              │
│  • Cria sessão                                                   │
│  • Valida eventos                                                │
│  • Calcula agregações                                            │
└────────────────────┼──────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              BANCO DE DADOS POSTGRESQL                          │
│                                                                  │
│  ┌──────────┐      ┌──────────┐      ┌──────────────┐          │
│  │  totems  │◄─────│ sessions │◄─────│sensor_events │          │
│  └──────────┘      └────┬─────┘      └──────────────┘          │
│                         │                                        │
│                         ▼                                        │
│              ┌──────────────────────┐                           │
│              │session_aggregates    │                           │
│              └──────────────────────┘                           │
└────────────────────┼──────────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ LIMPEZA DE DADOS │    │  ANÁLISE DE      │
│                  │    │  DADOS           │
│ • Remove dups    │    │                  │
│ • Valida valores │    │ • Estatísticas   │
│ • Padroniza      │    │ • Padrões        │
│ • Retenção       │    │ • Engajamento    │
└──────────────────┘    └────────┬─────────┘
                                 │
                                 ▼
                    ┌──────────────────────┐
                    │  MACHINE LEARNING    │
                    │                      │
                    │ • Treinamento        │
                    │ • Classificação      │
                    │ • Predição           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     DASHBOARD        │
                    │                      │
                    │ • Visualizações      │
                    │ • Métricas           │
                    │ • Relatórios         │
                    └──────────────────────┘
```

## Fluxo Detalhado por Etapa

### Etapa 1: Geração de Eventos
```
Sensor Simulator
    │
    ├─> generate_touch_event()
    │   └─> Retorna: {event_type, value, duration, touch_type}
    │
    ├─> generate_presence_event()
    │   └─> Retorna: {event_type, value}
    │
    └─> generate_ldr_event()
        └─> Retorna: {event_type, value}
```

### Etapa 2: Coleta e Armazenamento
```
Data Collector
    │
    ├─> start_session()
    │   └─> Cria UUID, registra no BD
    │
    ├─> collect_and_store()
    │   ├─> Gera eventos via simulator
    │   ├─> Insere eventos no BD
    │   └─> Calcula agregações
    │
    └─> end_session()
        └─> Finaliza sessão, atualiza BD
```

### Etapa 3: Processamento
```
Data Cleaner
    │
    ├─> remove_duplicates()
    ├─> validate_sensor_values()
    ├─> standardize_timestamps()
    └─> remove_old_data()
```

### Etapa 4: Análise
```
Data Analyzer
    │
    ├─> load_data_to_dataframe()
    ├─> get_descriptive_stats()
    ├─> analyze_touch_patterns()
    ├─> analyze_temporal_patterns()
    └─> calculate_engagement_metrics()
```

### Etapa 5: Machine Learning
```
Touch Classifier
    │
    ├─> prepare_training_data()
    ├─> extract_features()
    ├─> train()
    │   ├─> Divide treino/teste
    │   ├─> Normaliza features
    │   └─> Treina Random Forest
    └─> predict()
        └─> Retorna tipo e confiança
```

### Etapa 6: Visualização
```
Dashboard (Streamlit)
    │
    ├─> Carrega dados do BD
    ├─> Gera gráficos (Plotly)
    ├─> Exibe métricas
    └─> Permite interação
```

## Exemplo de Transformação de Dados

### Entrada (Sensor)
```json
{
  "event_type": "touch",
  "value": 1,
  "duration": 1.2
}
```

### Processamento (Coletor)
```python
# Adiciona metadados
event['session_id'] = session_id
event['totem_id'] = totem_id
event['timestamp'] = datetime.now()
event['touch_type'] = 'long' if duration > 1.0 else 'short'
```

### Armazenamento (BD)
```sql
INSERT INTO sensor_events (
    session_id, totem_id, event_type, 
    value, duration, touch_type, timestamp
) VALUES (...)
```

### Agregação
```sql
INSERT INTO session_aggregates (
    session_id, total_touches, 
    long_touches, interaction_score
) VALUES (...)
```

### Análise
```python
# Calcula estatísticas
stats = {
    'total_touches': 5,
    'avg_duration': 1.1,
    'long_touches': 2
}
```

### Visualização
```python
# Gera gráfico
fig = px.histogram(durations, title='Distribuição de Duração')
```

## Fluxo de Dados em Tempo Real (Futuro)

```
[Sensor Real] → [ESP32] → [Wi-Fi] → [API REST] → [BD] → [Dashboard]
                                                          ↓
                                                    [Análise ML]
```

---

**Versão**: 2.0  
**Sprint**: 2

