
from psycopg.rows import dict_row

from src.database.connection import get_connection


def fetch_all(query):
    """Execute a read-only SQL query and return records."""
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def get_dashboard_metrics():
    """Return summary counts for the dashboard."""

    query = """
        SELECT
            (SELECT COUNT(*)
             FROM threat_indicators) AS indicators,

            (SELECT COUNT(*)
             FROM investigations
             WHERE status != 'Closed') AS investigations,

            (SELECT COUNT(*)
             FROM threat_indicators
             WHERE confidence >= 80) AS high_confidence
    """

    return fetch_all(query)[0]


def get_threat_indicators():
    """Retrieve stored threat intelligence records."""

    query = """
        SELECT
            t.indicator_id,
            t.indicator_value,
            t.indicator_type,
            s.source_name,
            t.confidence,
            t.description
        FROM threat_indicators t
        LEFT JOIN intelligence_sources s
            ON t.source_id = s.source_id
        ORDER BY t.confidence DESC NULLS LAST,
                 t.indicator_id
    """

    return fetch_all(query)


def get_investigations():
    """Retrieve active and closed investigations."""

    query = """
        SELECT
            investigation_id,
            title,
            description,
            status,
            priority,
            created_at
        FROM investigations
        ORDER BY created_at DESC, investigation_id DESC
    """

    return fetch_all(query)
