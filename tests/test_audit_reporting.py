
import psycopg
import pytest

from src.analyzers.case_management import (
    update_case,
    add_case_note,
    get_case_audit_history,
)
from src.reports.report_generator import (
    generate_case_report,
)


@pytest.fixture
def report_case():
    conn = psycopg.connect("dbname=gameshield_ti_test")

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database()")
            assert cursor.fetchone()[0] == "gameshield_ti_test"

            cursor.execute(
                """
                INSERT INTO intelligence_sources
                    (source_name)
                VALUES ('Audit Reporting Test Source')
                RETURNING source_id
                """
            )
            source_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO threat_indicators
                    (indicator_value, indicator_type, source_id)
                VALUES ('192.0.2.150', 'IPv4', %s)
                RETURNING indicator_id
                """,
                (source_id,),
            )
            indicator_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO security_events
                    (event_type, player_id, source_ip)
                VALUES ('failed_login', 'AUDIT_TEST', '192.0.2.150')
                RETURNING event_id
                """
            )
            event_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO automated_cases
                    (event_id, indicator_id, title)
                VALUES (%s, %s, 'Audit Test Case')
                RETURNING case_id
                """,
                (event_id, indicator_id),
            )
            case_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO case_evidence
                    (case_id, event_id, indicator_id)
                VALUES (%s, %s, %s)
                """,
                (case_id, event_id, indicator_id),
            )

        yield conn, case_id

    finally:
        conn.rollback()
        conn.close()


def test_case_update_creates_audit_record(report_case):
    conn, case_id = report_case

    assert update_case(
        case_id,
        "In Progress",
        "High",
        conn=conn,
        actor="Test Analyst",
    )

    history = get_case_audit_history(case_id, conn)

    assert len(history) == 1
    assert history[0]["action"] == "case_updated"
    assert history[0]["actor"] == "Test Analyst"
    assert history[0]["old_value"]["status"] == "Open"
    assert history[0]["new_value"]["status"] == "In Progress"


def test_note_creation_is_audited(report_case):
    conn, case_id = report_case

    add_case_note(
        case_id,
        "Test Analyst",
        "Reviewed supporting evidence.",
        conn,
    )

    history = get_case_audit_history(case_id, conn)

    assert len(history) == 1
    assert history[0]["action"] == "note_added"
    assert "note_id" in history[0]["new_value"]


def test_unchanged_case_has_no_audit_record(report_case):
    conn, case_id = report_case

    assert update_case(
        case_id,
        "Open",
        "Medium",
        conn=conn,
    )

    history = get_case_audit_history(case_id, conn)

    assert history == []


def test_report_contains_investigation_details(report_case):
    conn, case_id = report_case

    add_case_note(
        case_id,
        "Test Analyst",
        "Reviewed synthetic login activity.",
        conn,
    )

    report = generate_case_report(case_id, conn)

    assert "Audit Test Case" in report
    assert "192.0.2.150" in report
    assert "Review Score" in report
    assert "Reviewed synthetic login activity." in report
    assert "note_added" in report


def test_missing_case_raises_error(report_case):
    conn, _ = report_case

    with pytest.raises(ValueError):
        generate_case_report(-1, conn)
