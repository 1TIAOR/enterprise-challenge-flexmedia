# Código-Fonte - Totem Flexmedia

## Estrutura de Pastas

### `sensors/`
Simulador de sensores físicos (toque, presença PIR, LDR)
- `sensor_simulator.py`: Classe principal para simulação

### `database/`
Gerenciamento do banco de dados PostgreSQL
- `schema.sql`: Schema completo do banco
- `db_connection.py`: Gerenciador de conexão e operações
- `init_db.py`: Script de inicialização

### `analysis/`
Análise estatística dos dados coletados
- `data_analysis.py`: Estatísticas descritivas, padrões temporais, métricas de engajamento

### `ml/`
Modelos de Machine Learning
- `touch_classifier.py`: Classificador de tipo de toque (Random Forest)
- `models/`: Pasta para modelos treinados salvos

### `dashboard/`
Interface web interativa
- `app.py`: Dashboard Streamlit com visualizações

## Arquivos Principais na Raiz de `src/`

- `data_collector.py`: Integra sensores com banco de dados
- `data_cleaning.py`: Limpeza, validação e padronização de dados

## Como Usar

Consulte o [QUICK_START.md](../QUICK_START.md) para instruções rápidas de uso.

Para documentação completa, veja [TECHNICAL_DOCUMENTATION.md](../document/TECHNICAL_DOCUMENTATION.md).
