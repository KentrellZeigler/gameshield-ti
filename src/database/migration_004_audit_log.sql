
CREATE TABLE IF NOT EXISTS case_audit_log (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    case_id BIGINT NOT NULL
        REFERENCES automated_cases(case_id),

    action VARCHAR(50) NOT NULL,

    actor VARCHAR(100) NOT NULL,

    old_value JSONB,
    new_value JSONB,

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_audit_action CHECK (
        action IN (
            'case_updated',
            'note_added',
            'baseline_recorded'
        )
    )
);

CREATE INDEX IF NOT EXISTS idx_case_audit_history
    ON case_audit_log(case_id, created_at DESC);
