-- Tabela de Totems
CREATE TABLE IF NOT EXISTS totems (
    id SERIAL PRIMARY KEY,
    totem_id VARCHAR(50) UNIQUE NOT NULL,
    location VARCHAR(100),
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Sessões
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id UUID UNIQUE NOT NULL,
    totem_id VARCHAR(50) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    duration_seconds DECIMAL(10, 2),
    total_interactions INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (totem_id) REFERENCES totems(totem_id)
);

-- Tabela de Eventos de Sensores
CREATE TABLE IF NOT EXISTS sensor_events (
    id SERIAL PRIMARY KEY,
    session_id UUID,
    totem_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(20) NOT NULL, -- 'touch', 'presence', 'ldr'
    value INTEGER NOT NULL, -- 0 ou 1 para touch/presence, 0-1023 para LDR
    duration DECIMAL(10, 2), -- Duração do toque em segundos
    touch_type VARCHAR(10), -- 'short', 'long', 'none'
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (totem_id) REFERENCES totems(totem_id)
);

-- Tabela de Agregações por Sessão (para análise)
CREATE TABLE IF NOT EXISTS session_aggregates (
    id SERIAL PRIMARY KEY,
    session_id UUID UNIQUE NOT NULL,
    totem_id VARCHAR(50) NOT NULL,
    total_touches INTEGER DEFAULT 0,
    short_touches INTEGER DEFAULT 0,
    long_touches INTEGER DEFAULT 0,
    avg_presence_time DECIMAL(10, 2),
    avg_light_level DECIMAL(10, 2),
    session_duration DECIMAL(10, 2),
    interaction_score DECIMAL(5, 2), -- Score calculado de 0-100
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (totem_id) REFERENCES totems(totem_id)
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_sensor_events_session ON sensor_events(session_id);
CREATE INDEX IF NOT EXISTS idx_sensor_events_totem ON sensor_events(totem_id);
CREATE INDEX IF NOT EXISTS idx_sensor_events_timestamp ON sensor_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_events_type ON sensor_events(event_type);
CREATE INDEX IF NOT EXISTS idx_sessions_totem ON sessions(totem_id);
CREATE INDEX IF NOT EXISTS idx_sessions_started_at ON sessions(started_at);

-- View para análise de interações
CREATE OR REPLACE VIEW interaction_analysis AS
SELECT 
    s.session_id,
    s.totem_id,
    s.started_at,
    s.duration_seconds,
    sa.total_touches,
    sa.short_touches,
    sa.long_touches,
    sa.avg_light_level,
    sa.interaction_score,
    CASE 
        WHEN sa.interaction_score >= 70 THEN 'high'
        WHEN sa.interaction_score >= 40 THEN 'medium'
        ELSE 'low'
    END as engagement_level
FROM sessions s
LEFT JOIN session_aggregates sa ON s.session_id = sa.session_id
WHERE s.ended_at IS NOT NULL;

