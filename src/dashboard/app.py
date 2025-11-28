"""
Dashboard Interativo para Visualização de Métricas
Usando Streamlit para interface web simples
"""

import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database.db_connection import DatabaseManager
from src.analysis.data_analysis import DataAnalyzer
from src.ml.touch_classifier import TouchClassifier

# Configuração da página
st.set_page_config(
    page_title="Totem Flexmedia - Dashboard",
    page_icon="📊",
    layout="wide"
)

# Título
st.title("📊 Dashboard Totem Flexmedia")
st.markdown("---")

# Inicializa componentes
@st.cache_resource
def init_db():
    return DatabaseManager()

@st.cache_resource
def init_analyzer():
    return DataAnalyzer()

db = init_db()
analyzer = init_analyzer()

# Sidebar para filtros
st.sidebar.header("Filtros")
totem_id = st.sidebar.selectbox(
    "Totem",
    options=[None, "TOTEM-001", "TOTEM-002", "TOTEM-003"],
    format_func=lambda x: "Todos" if x is None else x
)

days = st.sidebar.slider("Período (dias)", 1, 90, 30)

# Botão para limpar cache
if st.sidebar.button("🔄 Atualizar Dados"):
    st.cache_data.clear()
    st.rerun()

# Carrega dados
@st.cache_data(ttl=60)
def load_data(totem_id, days):
    return analyzer.load_data_to_dataframe(totem_id, days)

df = load_data(totem_id, days)

if df.empty:
    st.warning("⚠️ Nenhum dado encontrado para o período selecionado.")
    st.info("💡 Execute o coletor de dados primeiro para gerar métricas.")
else:
    # Métricas principais
    st.header("📈 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_events = len(df)
    total_sessions = df['session_id'].nunique()
    touch_events = len(df[(df['event_type'] == 'touch') & (df['value'] == 1)])
    avg_light = df[df['event_type'] == 'ldr']['value'].mean() if 'ldr' in df['event_type'].values else 0
    
    with col1:
        st.metric("Total de Eventos", f"{total_events:,}")
    
    with col2:
        st.metric("Sessões", f"{total_sessions:,}")
    
    with col3:
        st.metric("Toques Detectados", f"{touch_events:,}")
    
    with col4:
        st.metric("Luminosidade Média", f"{avg_light:.0f}")
    
    st.markdown("---")
    
    # Gráficos
    st.header("📊 Visualizações")
    
    # Gráfico 1: Eventos por tipo ao longo do tempo
    st.subheader("Eventos por Tipo ao Longo do Tempo")
    
    if 'timestamp' in df.columns and not df.empty:
        # Filtra eventos que não são LDR para melhor visualização
        time_df = df[df['event_type'] != 'ldr'].copy()
        
        if not time_df.empty:
            try:
                # Garante que timestamp é datetime
                if not pd.api.types.is_datetime64_any_dtype(time_df['timestamp']):
                    time_df['timestamp'] = pd.to_datetime(time_df['timestamp'])
                
                # Calcula range de tempo dos dados
                time_range = (time_df['timestamp'].max() - time_df['timestamp'].min()).total_seconds()
                
                # Escolhe frequência de agrupamento baseado no range
                if time_range > 3600:  # Mais de 1 hora
                    freq = 'H'
                elif time_range > 60:  # Mais de 1 minuto
                    freq = 'min'
                else:  # Menos de 1 minuto - mostra todos os pontos
                    freq = None
                
                if freq:
                    time_grouped = time_df.groupby([pd.Grouper(key='timestamp', freq=freq), 'event_type']).size().reset_index(name='count')
                else:
                    # Sem agrupamento, mostra contagem por tipo
                    time_grouped = time_df.groupby(['timestamp', 'event_type']).size().reset_index(name='count')
                
                if not time_grouped.empty:
                    fig_time = px.line(
                        time_grouped,
                        x='timestamp',
                        y='count',
                        color='event_type',
                        title='Distribuição Temporal de Eventos',
                        labels={'count': 'Quantidade', 'timestamp': 'Data/Hora'},
                        markers=True
                    )
                    st.plotly_chart(fig_time, use_container_width=True)
                else:
                    st.info("📊 Não há dados suficientes para exibir o gráfico temporal.")
            except Exception as e:
                st.warning(f"⚠️ Erro ao processar dados temporais: {e}")
                st.error(str(e))
        else:
            st.info("📊 Não há eventos de toque ou presença para exibir.")
    else:
        st.info("📊 Dados de timestamp não disponíveis.")
    
    # Gráfico 2: Distribuição de toques
    st.subheader("Análise de Toques")
    
    col1, col2 = st.columns(2)
    
    with col1:
        touch_df = df[(df['event_type'] == 'touch') & (df['value'] == 1)]
        if not touch_df.empty and 'touch_type' in touch_df.columns:
            touch_types = touch_df['touch_type'].value_counts()
            fig_pie = px.pie(
                values=touch_types.values,
                names=touch_types.index,
                title='Distribuição de Tipos de Toque'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        if not touch_df.empty and 'duration' in touch_df.columns:
            durations = touch_df['duration'].dropna()
            if not durations.empty:
                fig_hist = px.histogram(
                    x=durations,
                    nbins=20,
                    title='Distribuição de Duração de Toques',
                    labels={'x': 'Duração (segundos)', 'y': 'Frequência'}
                )
                st.plotly_chart(fig_hist, use_container_width=True)
    
    # Gráfico 3: Padrão horário
    st.subheader("Padrão de Uso por Hora do Dia")
    
    if 'timestamp' in df.columns:
        df['hour'] = df['timestamp'].dt.hour
        hourly = df.groupby('hour').size().reset_index(name='count')
        
        fig_hourly = px.bar(
            hourly,
            x='hour',
            y='count',
            title='Eventos por Hora do Dia',
            labels={'hour': 'Hora', 'count': 'Quantidade de Eventos'}
        )
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    # Gráfico 4: Luminosidade ao longo do tempo
    st.subheader("Níveis de Luminosidade (LDR)")
    
    ldr_df = df[df['event_type'] == 'ldr'].copy()
    if not ldr_df.empty and 'timestamp' in ldr_df.columns:
        try:
            # Garante que timestamp é datetime
            if not pd.api.types.is_datetime64_any_dtype(ldr_df['timestamp']):
                ldr_df['timestamp'] = pd.to_datetime(ldr_df['timestamp'])
            
            # Calcula range de tempo dos dados
            time_range = (ldr_df['timestamp'].max() - ldr_df['timestamp'].min()).total_seconds()
            
            # Escolhe frequência de agrupamento baseado no range
            if time_range > 3600:  # Mais de 1 hora
                freq = 'H'
            elif time_range > 60:  # Mais de 1 minuto
                freq = 'min'
            else:  # Menos de 1 minuto - mostra todos os pontos
                freq = None
            
            if freq:
                ldr_grouped = ldr_df.groupby(pd.Grouper(key='timestamp', freq=freq))['value'].mean().reset_index()
            else:
                # Sem agrupamento, mostra todos os pontos ordenados
                ldr_grouped = ldr_df[['timestamp', 'value']].copy().sort_values('timestamp')
            
            if not ldr_grouped.empty:
                fig_ldr = px.line(
                    ldr_grouped,
                    x='timestamp',
                    y='value',
                    title='Luminosidade ao Longo do Tempo',
                    labels={'value': 'Luminosidade (0-1023)', 'timestamp': 'Data/Hora'},
                    markers=True
                )
                fig_ldr.update_traces(mode='lines+markers')
                st.plotly_chart(fig_ldr, use_container_width=True)
            else:
                st.info("📊 Não há dados de luminosidade suficientes para exibir o gráfico.")
        except Exception as e:
            st.warning(f"⚠️ Erro ao processar dados de luminosidade: {e}")
            st.info(f"Total de registros LDR: {len(ldr_df)}")
            # Fallback: tenta mostrar dados brutos
            try:
                ldr_simple = ldr_df[['timestamp', 'value']].head(100).copy()
                if not ldr_simple.empty:
                    st.dataframe(ldr_simple)
            except:
                pass
    else:
        st.info("📊 Não há dados de luminosidade (LDR) disponíveis.")
    
    # Relatório de análise
    st.markdown("---")
    st.header("📋 Relatório de Análise")
    
    if st.button("Gerar Relatório Completo"):
        with st.spinner("Gerando relatório..."):
            report = analyzer.generate_full_report(totem_id)
            
            st.subheader("Estatísticas Descritivas")
            st.json(report.get('descriptive_stats', {}))
            
            st.subheader("Padrões de Toque")
            st.json(report.get('touch_patterns', {}))
            
            st.subheader("Métricas de Engajamento")
            st.json(report.get('engagement_metrics', {}))
    
    # Seção de ML
    st.markdown("---")
    st.header("🤖 Classificação de Toques (ML)")
    
    if st.button("Treinar Modelo"):
        with st.spinner("Treinando modelo..."):
            classifier = TouchClassifier()
            results = classifier.train()
            
            st.success("✅ Modelo treinado com sucesso!")
            st.metric("Acurácia", f"{results['accuracy']:.2%}")
            
            classifier.save_model('src/ml/models/touch_classifier.pkl')
    
    # Teste de predição
    st.subheader("Testar Predição")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        duration = st.number_input("Duração do Toque (s)", 0.1, 3.0, 1.0, 0.1)
    
    with col2:
        session_duration = st.number_input("Duração da Sessão (s)", 10, 300, 60, 10)
    
    with col3:
        total_touches = st.number_input("Total de Toques na Sessão", 1, 20, 3, 1)
    
    if st.button("Predizer Tipo de Toque"):
        try:
            classifier = TouchClassifier()
            classifier.load_model('src/ml/models/touch_classifier.pkl')
            
            prediction = classifier.predict(
                duration=duration,
                session_duration=session_duration,
                total_touches=total_touches
            )
            
            st.success(f"**Predição:** {prediction['predicted_type'].upper()}")
            st.info(f"Confiança: {prediction['confidence']:.1%}")
            st.json(prediction)
        except Exception as e:
            st.error(f"Erro ao fazer predição: {e}")

# Rodapé
st.markdown("---")
st.markdown("**Totem Flexmedia** - Dashboard de Análise de Dados | Sprint 2")

