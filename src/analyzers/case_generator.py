
from contextlib import nullcontext

from psycopg.rows import dict_row

from src.database.connection import get_connection
from src.analyzers.correlation import (
    correlate_ip_indicators,
)



def generate_cases(conn=None):
    """
    Create cases and synchronize supporting evidence.

    Existing cases are reused.
    Duplicate evidence is ignored.

    Returns the number of newly created cases.
    """

    context = (
        nullcontext(conn)
        if conn is not None
        else get_connection()
    )

    with context as connection:
        matches = correlate_ip_indicators(connection)
        created = 0
        case_ids = {}

        with connection.cursor() as cursor:

            for match in matches:
                event_id = match["event_id"]
                indicator_id = match["indicator_id"]

                if event_id not in case_ids:
                    title = (
                        f"Security Event Review - {event_id}"
                    )

                    cursor.execute(
                        """
                        INSERT INTO automated_cases
                            (event_id, indicator_id, title,
                             status, priority)
                        VALUES (%s, %s, %s, 'Open', 'Medium')
                        ON CONFLICT (event_id)
                        DO NOTHING
                        RETURNING case_id
                        """,
                        (event_id, indicator_id, title),
                    )

                    result = cursor.fetchone()

                    if result is not None:
                        case_id = result[0]
                        created += 1
                    else:
                        cursor.execute(
                            """
                            SELECT case_id
                            FROM automated_cases
                            WHERE event_id = %s
                            """,
                            (event_id,),
                        )

                        case_id = cursor.fetchone()[0]

                    case_ids[event_id] = case_id

                case_id = case_ids[event_id]

                cursor.execute(
                    """
                    INSERT INTO case_evidence
                        (case_id, event_id,
                         indicator_id, match_type)
                    VALUES (%s, %s, %s, 'exact_ip')
                    ON CONFLICT
                        (case_id, event_id, indicator_id)
                    DO NOTHING
                    """,
                    (case_id, event_id, indicator_id),
                )

        if conn is None:
            connection.commit()

    return created


def get_automated_cases(conn=None):
    """Retrieve generated cases with supporting evidence."""

    query = """
        SELECT
            c.case_id,
            c.title,
            c.status,
            c.priority,
            e.event_type,
            e.player_id,
            host(e.source_ip) AS source_ip,
            t.indicator_value,
            s.source_name,
            c.created_at
        FROM automated_cases c
        JOIN security_events e
            ON c.event_id = e.event_id
        JOIN threat_indicators t
            ON c.indicator_id = t.indicator_id
        LEFT JOIN intelligence_sources s
            ON t.source_id = s.source_id
        ORDER BY c.created_at DESC, c.case_id DESC
    """

    context = (
        nullcontext(conn)
        if conn is not None
        else get_connection()
    )

    with context as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def get_case_evidence(case_id, conn=None):
    """Retrieve evidence associated with an investigation."""

    query = """
        SELECT
            ce.evidence_id,
            ce.case_id,
            ce.indicator_id,
            ce.match_type,
            ce.discovered_at,
            e.event_id,
            e.event_type,
            e.player_id,
            host(e.source_ip) AS source_ip,
            e.event_time,
            t.indicator_value,
            t.indicator_type,
            t.confidence,
            t.description,
            s.source_name
        FROM case_evidence ce
        JOIN security_events e
            ON ce.event_id = e.event_id
        JOIN threat_indicators t
            ON ce.indicator_id = t.indicator_id
        LEFT JOIN intelligence_sources s
            ON t.source_id = s.source_id
        WHERE ce.case_id = %s
        ORDER BY ce.discovered_at DESC,
                 ce.evidence_id DESC
    """

    context = (
        nullcontext(conn)
        if conn is not None
        else get_connection()
    )

    with context as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, (case_id,))
            return cursor.fetchall()

if __name__ == "__main__":
    created = generate_cases()
    print(f"New investigation cases created: {created}")

