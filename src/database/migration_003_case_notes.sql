
CREATE TABLE IF NOT EXISTS case_notes (
    note_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    case_id BIGINT NOT NULL
        REFERENCES automated_cases(case_id)
        ON DELETE CASCADE,

    author VARCHAR(100) NOT NULL,

    note_text TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT note_text_not_empty
        CHECK (length(trim(note_text)) > 0)
);

CREATE INDEX IF NOT EXISTS idx_case_notes_case
    ON case_notes(case_id, created_at DESC);
