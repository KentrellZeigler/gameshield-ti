
CREATE TABLE IF NOT EXISTS case_evidence (
    evidence_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    case_id BIGINT NOT NULL
        REFERENCES automated_cases(case_id)
        ON DELETE CASCADE,

    event_id BIGINT NOT NULL
        REFERENCES security_events(event_id),

    indicator_id BIGINT NOT NULL
        REFERENCES threat_indicators(indicator_id),

    match_type VARCHAR(50) NOT NULL DEFAULT 'exact_ip',

    discovered_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_case_evidence
        UNIQUE (case_id, event_id, indicator_id)
);

CREATE INDEX IF NOT EXISTS idx_case_evidence_case
    ON case_evidence(case_id);
