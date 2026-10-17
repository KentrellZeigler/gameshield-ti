
CREATE TABLE IF NOT EXISTS automated_cases (
    case_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    event_id BIGINT NOT NULL UNIQUE
        REFERENCES security_events(event_id),

    indicator_id BIGINT NOT NULL
        REFERENCES threat_indicators(indicator_id),

    title VARCHAR(200) NOT NULL,

    status VARCHAR(30) NOT NULL DEFAULT 'Open',
    priority VARCHAR(20) NOT NULL DEFAULT 'Medium',

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CHECK (status IN ('Open', 'In Progress', 'Closed')),
    CHECK (priority IN ('Low', 'Medium', 'High', 'Critical'))
);
