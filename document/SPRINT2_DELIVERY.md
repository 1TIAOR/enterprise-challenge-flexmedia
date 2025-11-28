# Entrega Sprint 2 - Totem Flexmedia

## Resumo da Implementação

Esta sprint implementa a integração entre sensores simulados, banco de dados SQL e análise de dados com Python, atendendo todos os requisitos técnicos e funcionais solicitados.

---

## ✅ Requisitos Atendidos

### 1. Integração entre Sensores, Análise Estatística e Banco de Dados SQL
- ✅ Simulador de sensores (toque, presença PIR, LDR)
- ✅ Schema SQL completo (PostgreSQL)
- ✅ Coletor de dados que integra sensores → banco
- ✅ Scripts de análise estatística

### 2. Registro e Estruturação de Dados
- ✅ Tabelas: `totems`, `sessions`, `sensor_events`, `session_aggregates`
- ✅ Registro de ativações, tempo de permanência, respostas
- ✅ Agregações calculadas automaticamente

### 3. Visualizações e Dashboard
- ✅ Dashboard interativo com Streamlit
- ✅ Gráficos com Plotly (linhas, barras, pizza, histogramas)
- ✅ Métricas em tempo real
- ✅ Filtros por totem e período

### 4. Machine Learning Supervisionado
- ✅ Modelo Random Forest para classificar tipo de toque
- ✅ Features: duração, contexto da sessão, luminosidade
- ✅ Treinamento, avaliação e predição implementados
- ✅ Geração de dados sintéticos quando necessário

### 5. Limpeza e Organização de Dados
- ✅ Remoção de duplicações
- ✅ Validação de valores (0/1 para binários, 0-1023 para LDR)
- ✅ Padronização de timestamps
- ✅ Relatório de qualidade de dados

---

## 📁 Estrutura de Arquivos

```
src/
├── sensors/
│   └── sensor_simulator.py      # Simulador de sensores
├── database/
│   ├── schema.sql                # Schema do banco
│   ├── db_connection.py          # Gerenciador de conexão
│   └── init_db.py                # Script de inicialização
├── data_collector.py              # Integração sensores → BD
├── data_cleaning.py               # Limpeza e validação
├── analysis/
│   └── data_analysis.py           # Análise estatística
├── ml/
│   └── touch_classifier.py       # Modelo de ML
└── dashboard/
    └── app.py                     # Dashboard Streamlit
```

---

## 🔄 Fluxo de Dados Implementado

```
1. Sensores Simulados
   ↓ (gera eventos)
2. Coletor de Dados
   ↓ (valida e processa)
3. Banco de Dados PostgreSQL
   ↓ (armazena)
4. Limpeza de Dados
   ↓ (valida e corrige)
5. Análise Estatística
   ↓ (calcula métricas)
6. Modelo de ML
   ↓ (classifica)
7. Dashboard
   ↓ (visualiza)
```

---

## 📊 Exemplos de Dados Coletados

### Evento de Toque
```json
{
  "event_type": "touch",
  "timestamp": "2025-01-15T14:30:00Z",
  "value": 1,
  "duration": 1.2,
  "touch_type": "long",
  "totem_id": "TOTEM-001"
}
```

### Evento de Presença
```json
{
  "event_type": "presence",
  "timestamp": "2025-01-15T14:30:05Z",
  "value": 1,
  "totem_id": "TOTEM-001"
}
```

### Evento LDR
```json
{
  "event_type": "ldr",
  "timestamp": "2025-01-15T14:30:10Z",
  "value": 650,
  "totem_id": "TOTEM-001"
}
```

---

## 🎯 Funcionalidades do Dashboard

1. **Métricas Principais**
   - Total de eventos
   - Número de sessões
   - Toques detectados
   - Luminosidade média

2. **Visualizações**
   - Eventos por tipo ao longo do tempo
   - Distribuição de tipos de toque
   - Padrão de uso por hora do dia
   - Níveis de luminosidade

3. **Análise**
   - Relatório completo de análise
   - Estatísticas descritivas
   - Métricas de engajamento

4. **Machine Learning**
   - Treinamento de modelo
   - Teste de predição interativa

---

## 🤖 Modelo de Machine Learning

### Características
- **Algoritmo**: Random Forest Classifier
- **Features**: duração, duração da sessão, total de toques, luminosidade média, tempo na sessão
- **Target**: Tipo de toque (short/long)
- **Avaliação**: Acurácia, Precision, Recall, F1-Score

### Exemplo de Uso
```python
classifier = TouchClassifier()
classifier.train()
prediction = classifier.predict(duration=1.2, session_duration=60)
# Retorna: {'predicted_type': 'long', 'confidence': 0.85}
```

---

## 📈 Análises Implementadas

1. **Estatísticas Descritivas**
   - Contagem por tipo de evento
   - Taxa de ativação
   - Média, mediana, desvio padrão
   - Quartis

2. **Padrões Temporais**
   - Distribuição por hora do dia
   - Distribuição por dia da semana
   - Identificação de horários de pico

3. **Análise de Toques**
   - Distribuição de tipos
   - Duração média, mediana, min, max
   - Padrões de interação

4. **Métricas de Engajamento**
   - Toques médios por sessão
   - Taxa de engajamento
   - Sessões de alto/baixo engajamento

---

## 🧹 Limpeza de Dados

### Operações Implementadas
1. Remoção de duplicados (baseado em session_id, event_type, timestamp)
2. Validação de valores:
   - Touch/Presence: deve ser 0 ou 1
   - LDR: deve estar entre 0 e 1023
3. Padronização de timestamps (UTC)
4. Retenção de dados (remove dados >90 dias)

### Relatório de Qualidade
- Total de registros
- Registros por tipo
- Registros com problemas
- Score de qualidade (0-100%)

---

## 🚀 Como Executar

### 1. Setup Inicial
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env com credenciais do PostgreSQL

# Inicializar banco
python src/database/init_db.py
```

### 2. Gerar Dados de Exemplo
```bash
python scripts/generate_sample_data.py --sessions 10 --duration 30
```

### 3. Executar Análises
```bash
# Limpeza de dados
python src/data_cleaning.py

# Análise estatística
python src/analysis/data_analysis.py

# Treinar modelo ML
python src/ml/touch_classifier.py
```

### 4. Abrir Dashboard
```bash
streamlit run src/dashboard/app.py
```

---

## 📝 Documentação Adicional

- **Documentação Técnica Completa**: `document/TECHNICAL_DOCUMENTATION.md`
- **Schema SQL**: `src/database/schema.sql`
- **Exemplos de Código**: Ver docstrings nos arquivos Python

---

## 🎥 Demonstração

Para a demonstração em vídeo, seguir este roteiro:

1. **Setup** (30s)
   - Mostrar estrutura do projeto
   - Inicializar banco de dados

2. **Coleta de Dados** (1min)
   - Executar simulador de sensores
   - Mostrar eventos sendo gerados
   - Mostrar dados sendo inseridos no banco

3. **Limpeza e Validação** (30s)
   - Executar script de limpeza
   - Mostrar relatório de qualidade

4. **Análise** (1min)
   - Executar análise estatística
   - Mostrar resultados

5. **Machine Learning** (1min)
   - Treinar modelo
   - Mostrar métricas de avaliação
   - Fazer predições de exemplo

6. **Dashboard** (1min)
   - Abrir dashboard
   - Navegar pelas visualizações
   - Mostrar relatórios
   - Testar predição ML

7. **Conclusão** (30s)
   - Resumo do que foi implementado
   - Próximos passos

**Total**: ~5 minutos

---

## ✅ Checklist de Entrega

- [x] Repositório GitHub privado atualizado
- [x] Códigos e scripts implementados
- [x] Diagramas e visualizações (no dashboard)
- [x] README detalhado
- [x] Documentação técnica completa
- [x] Descrição da arquitetura
- [x] Exemplo de fluxo de dados documentado
- [x] Prints de execução (preparados para vídeo)
- [x] Sistema funcional e testado

---

**Versão**: 2.0  
**Data**: Janeiro 2025  
**Sprint**: 2

