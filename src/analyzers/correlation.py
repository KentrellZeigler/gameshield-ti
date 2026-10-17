
from contextlib import nullcontext

from psycopg.rows import dict_row

from src.database.connection import get_connection


CORRELATION_QUERY = """
    SELECT
        e.event_id,
        e.event_type,
        e.player_id,
        host(e.source_ip) AS source_ip,
        e.event_time,
        t.indicator_id,
        t.indicator_type,
        t.confidence,
        s.source_name,
        t.description,
        e.investigation_id
    FROM security_events e
    JOIN threat_indicators t
      ON host(e.source_ip) = t.indicator_value
     AND t.indicator_type IN ('IPv4', 'IPv6')
    LEFT JOIN intelligence_sources s
      ON t.source_id = s.source_id
    WHERE e.source_ip IS NOT NULL
    ORDER BY e.event_time DESC, e.event_id DESC
"""


def correlate_ip_indicators(conn=None):
    """Find exact IP matches in security events."""

    # A supplied test connection stays open.
    # Otherwise, manage our own connection.
    context = (
        nullcontext(conn)
        if conn is not None
        else get_connection()
    )

    with context as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(CORRELATION_QUERY)
            return cursor.fetchall()


if __name__ == "__main__":
    matches = correlate_ip_indicators()

    print(f"Found {len(matches)} correlation matches.")

    for match in matches:
        print(
            f"Event {match['event_id']} | "
            f"Player: {match['player_id']} | "
            f"IP: {match['source_ip']} | "
            f"Source: {match['source_name']}"
        )
