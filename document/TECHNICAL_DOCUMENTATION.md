# Documentação Técnica - Sprint 2
## Totem Flexmedia - Integração de Sensores e Análise de Dados

---

## 1. Visão Geral da Arquitetura

### 1.1 Componentes Principais

O sistema é composto pelos seguintes módulos:

1. **Simulador de Sensores** (`src/sensors/sensor_simulator.py`)
   - Simula sensores físicos (toque, presença PIR, LDR)
   - Gera eventos em tempo real ou batch
   - Cria sessões de interação

2. **Gerenciador de Banco de Dados** (`src/database/`)
   - Schema SQL (PostgreSQL)
   - Conexão e operações CRUD
   - Agregações e views

3. **Coletor de Dados** (`src/data_collector.py`)
   - Integra sensores com banco de dados
   - Processa e armazena eventos
   - Calcula métricas de sessão

4. **Limpeza de Dados** (`src/data_cleaning.py`)
   - Remove duplicações
   - Valida e corrige valores
   - Padroniza formatos

5. **Análise Estatística** (`src/analysis/data_analysis.py`)
   - Estatísticas descritivas
   - Análise de padrões temporais
   - Métricas de engajamento

6. **Machine Learning** (`src/ml/touch_classifier.py`)
   - Modelo supervisionado (Random Forest)
   - Classificação de tipo de toque
   - Treinamento e predição

7. **Dashboard** (`src/dashboard/app.py`)
   - Interface web (Streamlit)
   - Visualizações interativas
   - Relatórios em tempo real

---

## 2. Fluxo de Dados

### 2.1 Pipeline Completo

```
[Sensores Simulados] 
    ↓
[Coletor de Dados]
    ↓
[Validação e Limpeza]
    ↓
[Banco de Dados PostgreSQL]
    ↓
[Análise Estatística]
    ↓
[Modelo de ML]
    ↓
[Dashboard/Visualizações]
```

### 2.2 Fluxo Detalhado por Etapa

#### Etapa 1: Coleta
1. Simulador gera eventos de sensores (toque, presença, LDR)
2. Eventos são agrupados por sessão
3. Cada evento contém: tipo, valor, timestamp, duração (se aplicável)

#### Etapa 2: Armazenamento
1. Sessão é criada no banco
2. Eventos são inseridos na tabela `sensor_events`
3. Agregações são calculadas e armazenadas em `session_aggregates`

#### Etapa 3: Processamento
1. Dados são validados e limpos
2. Duplicações são removidas
3. Valores inválidos são corrigidos

#### Etapa 4: Análise
1. Estatísticas descritivas são calculadas
2. Padrões temporais são identificados
3. Métricas de engajamento são geradas

#### Etapa 5: Machine Learning
1. Features são extraídas dos dados
2. Modelo é treinado (ou carregado)
3. Predições são feitas para novos eventos

#### Etapa 6: Visualização
1. Dashboard carrega dados do banco
2. Gráficos são gerados dinamicamente
3. Relatórios são exibidos

---

## 3. Estrutura do Banco de Dados

### 3.1 Tabelas Principais

#### `totems`
Armazena informações dos totens físicos.

```sql
- id (SERIAL PRIMARY KEY)
- totem_id (VARCHAR, UNIQUE)
- location (VARCHAR)
- installed_at (TIMESTAMP)
- status (VARCHAR)
```

#### `sessions`
Representa uma sessão de interação com o totem.

```sql
- id (SERIAL PRIMARY KEY)
- session_id (UUID, UNIQUE)
- totem_id (VARCHAR, FK)
- started_at (TIMESTAMP)
- ended_at (TIMESTAMP)
- duration_seconds (DECIMAL)
- total_interactions (INTEGER)
```

#### `sensor_events`
Armazena todos os eventos de sensores.

```sql
- id (SERIAL PRIMARY KEY)
- session_id (UUID, FK)
- totem_id (VARCHAR, FK)
- event_type (VARCHAR) -- 'touch', 'presence', 'ldr'
- value (INTEGER) -- 0/1 para touch/presence, 0-1023 para LDR
- duration (DECIMAL) -- Duração do toque
- touch_type (VARCHAR) -- 'short', 'long', 'none'
- timestamp (TIMESTAMP)
```

#### `session_aggregates`
Agregações calculadas por sessão.

```sql
- id (SERIAL PRIMARY KEY)
- session_id (UUID, FK)
- totem_id (VARCHAR, FK)
- total_touches (INTEGER)
- short_touches (INTEGER)
- long_touches (INTEGER)
- avg_presence_time (DECIMAL)
- avg_light_level (DECIMAL)
- session_duration (DECIMAL)
- interaction_score (DECIMAL) -- 0-100
```

### 3.2 Views

#### `interaction_analysis`
View que agrega dados de sessões e agregações para análise rápida.

---

## 4. Modelo de Machine Learning

### 4.1 Objetivo
Classificar tipo de toque (curto ou longo) baseado em features extraídas dos dados.

### 4.2 Features Utilizadas
- `duration`: Duração do toque em segundos
- `session_duration`: Duração total da sessão
- `total_touches`: Número total de toques na sessão
- `avg_light_level`: Nível médio de luminosidade
- `time_in_session`: Tempo decorrido na sessão até o toque

### 4.3 Algoritmo
- **Random Forest Classifier**
- 100 árvores
- Profundidade máxima: 10
- Validação: 80% treino, 20% teste

### 4.4 Métricas de Avaliação
- Acurácia
- Precision, Recall, F1-Score
- Matriz de Confusão

---

## 5. Análise Estatística

### 5.1 Estatísticas Descritivas
- Contagem de eventos por tipo
- Taxa de ativação (para eventos binários)
- Média, mediana, desvio padrão (para valores contínuos)
- Quartis (para LDR)

### 5.2 Análise de Padrões
- **Temporais**: Distribuição por hora do dia, dia da semana
- **Toques**: Distribuição de tipos, duração média
- **Engajamento**: Taxa de interação, sessões de alto/baixo engajamento

---

## 6. Limpeza e Validação de Dados

### 6.1 Operações de Limpeza
1. **Remoção de Duplicados**: Baseado em session_id, event_type, timestamp
2. **Validação de Valores**:
   - Touch/Presence: deve ser 0 ou 1
   - LDR: deve estar entre 0 e 1023
3. **Padronização**: Timestamps em UTC
4. **Retenção**: Remove dados antigos (>90 dias)

### 6.2 Relatório de Qualidade
- Total de registros
- Registros por tipo
- Registros com problemas
- Score de qualidade (0-100%)

---

## 7. Dashboard

### 7.1 Funcionalidades
- Visualização de métricas principais
- Gráficos interativos (Plotly)
- Filtros por totem e período
- Relatórios de análise
- Teste de modelo ML

### 7.2 Visualizações
1. **Eventos por Tipo ao Longo do Tempo**: Gráfico de linhas
2. **Distribuição de Toques**: Gráfico de pizza e histograma
3. **Padrão de Uso por Hora**: Gráfico de barras
4. **Níveis de Luminosidade**: Gráfico de linhas temporal

---

## 8. Exemplos de Uso

### 8.1 Coleta de Dados
```python
from src.data_collector import DataCollector

collector = DataCollector("TOTEM-001")
stats = collector.collect_and_store(duration_seconds=60)
```

### 8.2 Limpeza de Dados
```python
from src.data_cleaning import DataCleaner

cleaner = DataCleaner()
results = cleaner.clean_all()
report = cleaner.get_data_quality_report()
```

### 8.3 Análise
```python
from src.analysis.data_analysis import DataAnalyzer

analyzer = DataAnalyzer()
report = analyzer.generate_full_report("TOTEM-001")
```

### 8.4 Machine Learning
```python
from src.ml.touch_classifier import TouchClassifier

classifier = TouchClassifier()
classifier.train()
prediction = classifier.predict(duration=1.2, session_duration=60)
```

### 8.5 Dashboard
```bash
streamlit run src/dashboard/app.py
```

---

## 9. Tecnologias Utilizadas

| Componente | Tecnologia |
|------------|-----------|
| Linguagem | Python 3.10+ |
| Banco de Dados | PostgreSQL |
| ML Framework | Scikit-learn |
| Visualização | Plotly, Streamlit |
| Análise | Pandas, NumPy |

---

## 10. Próximos Passos (Sprint 3)

- Integração com sensores reais (ESP32)
- API REST para recebimento de eventos
- Processamento em tempo real
- Modelos de IA mais avançados
- Integração com visão computacional

---

## 11. Considerações de Escalabilidade

### 11.1 Banco de Dados
- Índices criados para otimizar consultas
- Views para agregações rápidas
- Política de retenção de dados (90 dias)

### 11.2 Processamento
- Cache de dados no dashboard
- Processamento assíncrono (futuro)
- Batch processing para grandes volumes

### 11.3 Manutenibilidade
- Código modular e bem documentado
- Separação de responsabilidades
- Fácil extensão para novos sensores

---

## 12. Segurança e Privacidade

- Dados anonimizados (sem informações pessoais)
- Conexões seguras (HTTPS em produção)
- Validação de entrada
- Retenção controlada de dados

---

**Versão**: 2.0  
**Data**: 2025-01  
**Sprint**: 2

