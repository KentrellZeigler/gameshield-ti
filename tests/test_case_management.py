
import psycopg
import pytest

from src.analyzers.case_management import (
    update_case,
    add_case_note,
    get_case_notes,
)


@pytest.fixture
def test_case():
    """Create an isolated test case and roll back all changes."""

    conn = psycopg.connect("dbname=gameshield_ti_test")

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database()")
            assert cursor.fetchone()[0] == "gameshield_ti_test"

            cursor.execute(
                """
                INSERT INTO security_events
                    (event_type, player_id, source_ip)
                VALUES ('failed_login', 'CASE_MGMT_TEST', %s)
                RETURNING event_id
                """,
                ("192.0.2.201",),
            )
            event_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO intelligence_sources
                    (source_name)
                VALUES ('Case Management Test Source')
                ON CONFLICT (source_name)
                DO UPDATE SET source_name = EXCLUDED.source_name
                RETURNING source_id
                """
            )
            source_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO threat_indicators
                    (indicator_value, indicator_type, source_id)
                VALUES (%s, 'IPv4', %s)
                ON CONFLICT (
                    indicator_type,
                    indicator_value,
                    source_id
                )
                DO UPDATE SET
                    indicator_value = EXCLUDED.indicator_value
                RETURNING indicator_id
                """,
                ("192.0.2.201", source_id),
            )
            indicator_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO automated_cases
                    (event_id, indicator_id, title)
                VALUES (%s, %s, 'Case Management Test')
                RETURNING case_id
                """,
                (event_id, indicator_id),
            )
            case_id = cursor.fetchone()[0]

        yield conn, case_id

    finally:
        conn.rollback()
        conn.close()


def test_update_case(test_case):
    conn, case_id = test_case

    assert update_case(
        case_id,
        "In Progress",
        "High",
        conn,
    )

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT status, priority
            FROM automated_cases
            WHERE case_id = %s
            """,
            (case_id,),
        )
        status, priority = cursor.fetchone()

    assert status == "In Progress"
    assert priority == "High"


def test_add_and_retrieve_note(test_case):
    conn, case_id = test_case

    note_id = add_case_note(
        case_id,
        "Test Analyst",
        "Reviewed the synthetic evidence.",
        conn,
    )

    notes = get_case_notes(case_id, conn)

    assert note_id is not None
    assert len(notes) == 1
    assert notes[0]["author"] == "Test Analyst"
    assert notes[0]["note_text"] == (
        "Reviewed the synthetic evidence."
    )


def test_reject_invalid_status(test_case):
    conn, case_id = test_case

    with pytest.raises(ValueError):
        update_case(case_id, "Invalid", "High", conn)


def test_reject_empty_note(test_case):
    conn, case_id = test_case

    with pytest.raises(ValueError):
        add_case_note(case_id, "Test Analyst", "   ", conn)


def test_reject_invalid_priority(test_case):
    conn, case_id = test_case

    with pytest.raises(ValueError):
        update_case(case_id, "Open", "Urgent", conn)
