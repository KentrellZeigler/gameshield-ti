
CREATE TABLE IF NOT EXISTS intelligence_sources (
    source_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_name VARCHAR(150) NOT NULL UNIQUE,
    source_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS threat_indicators (
    indicator_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    indicator_value TEXT NOT NULL,
    indicator_type VARCHAR(50) NOT NULL,
    source_id BIGINT REFERENCES intelligence_sources(source_id),
    confidence INTEGER CHECK (confidence BETWEEN 0 AND 100),
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (indicator_type, indicator_value, source_id)
);

CREATE TABLE IF NOT EXISTS investigations (
    investigation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'Open',
    priority VARCHAR(20) NOT NULL DEFAULT 'Medium',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (status IN ('Open', 'In Progress', 'Closed')),
    CHECK (priority IN ('Low', 'Medium', 'High', 'Critical'))
);

CREATE TABLE IF NOT EXISTS security_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    player_id VARCHAR(100),
    source_ip INET,
    event_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details JSONB,
    investigation_id BIGINT REFERENCES investigations(investigation_id)
);

CREATE INDEX IF NOT EXISTS idx_events_time
ON security_events(event_time);

CREATE INDEX IF NOT EXISTS idx_events_ip
ON security_events(source_ip);
