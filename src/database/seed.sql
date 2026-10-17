
-- GameShield TI: Synthetic Development Data
-- All indicators and investigations are fictional.

BEGIN;

-- 1. Create a fictional intelligence source

INSERT INTO intelligence_sources
    (source_name, source_url)
VALUES
    ('GameShield Synthetic Lab', NULL)
ON CONFLICT (source_name) DO NOTHING;


-- 2. Insert example threat indicators
-- IPs belong to documentation-only address ranges.

INSERT INTO threat_indicators
    (indicator_value, indicator_type, source_id,
     confidence, description)
SELECT
    sample.indicator_value,
    sample.indicator_type,
    s.source_id,
    sample.confidence,
    sample.description
FROM (
    VALUES
    ('192.0.2.10', 'IPv4', 90,
     'Simulated credential stuffing source'),
    ('198.51.100.25', 'IPv4', 85,
     'Simulated suspicious login activity'),
    ('203.0.113.40', 'IPv4', 95,
     'Simulated coordinated account abuse'),
    ('203.0.113.55', 'IPv4', 40,
     'Simulated unusual connection activity'),
    ('198.51.100.88', 'IPv4', 65,
     'Simulated repeated authentication failures')
) AS sample (
    indicator_value,
    indicator_type,
    confidence,
    description
)
CROSS JOIN intelligence_sources s
WHERE s.source_name = 'GameShield Synthetic Lab'
ON CONFLICT
    (indicator_type, indicator_value, source_id)
DO NOTHING;


-- 3. Create fictional investigation cases

INSERT INTO investigations
    (title, description, status, priority)
SELECT
    'Coordinated Account Abuse',
    'Investigation of simulated linked player accounts',
    'Open',
    'High'
WHERE NOT EXISTS (
    SELECT 1 FROM investigations
    WHERE title = 'Coordinated Account Abuse'
);

INSERT INTO investigations
    (title, description, status, priority)
SELECT
    'Suspicious Login Activity',
    'Investigation of simulated authentication failures',
    'In Progress',
    'Medium'
WHERE NOT EXISTS (
    SELECT 1 FROM investigations
    WHERE title = 'Suspicious Login Activity'
);


-- 4. Create sample game security events

INSERT INTO security_events
    (event_type, player_id, source_ip, details,
     investigation_id)
SELECT
    'failed_login',
    'SIM_PLAYER_001',
    '192.0.2.10',
    '{"attempts": 15, "environment": "synthetic"}'::jsonb,
    i.investigation_id
FROM investigations i
WHERE i.title = 'Suspicious Login Activity'
AND NOT EXISTS (
    SELECT 1 FROM security_events e
    WHERE e.event_type = 'failed_login'
    AND e.player_id = 'SIM_PLAYER_001'
);

INSERT INTO security_events
    (event_type, player_id, source_ip, details,
     investigation_id)
SELECT
    'suspicious_transaction',
    'SIM_PLAYER_002',
    '203.0.113.40',
    '{"amount": 999999, "environment": "synthetic"}'::jsonb,
    i.investigation_id
FROM investigations i
WHERE i.title = 'Coordinated Account Abuse'
AND NOT EXISTS (
    SELECT 1 FROM security_events e
    WHERE e.event_type = 'suspicious_transaction'
    AND e.player_id = 'SIM_PLAYER_002'
);

COMMIT;
