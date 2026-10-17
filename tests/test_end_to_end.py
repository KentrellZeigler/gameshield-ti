
from src.database.connection import get_test_connection

from src.analyzers.correlation import correlate_ip_indicators
from src.analyzers.case_generator import (
    generate_cases,
    get_case_evidence,
)
from src.analyzers.priority_engine import calculate_case_priority
from src.analyzers.case_management import (
    update_case,
    add_case_note,
    get_case_audit_history,
)
from src.reports.report_generator import generate_case_report


def test_complete_investigation_workflow():
    conn = get_test_connection()

    try:
        # 1. Create synthetic intelligence and event.
        with conn.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO intelligence_sources (source_name)
                VALUES ('E2E Synthetic Test Source')
                RETURNING source_id
                """
            )
            source_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO threat_indicators
                    (indicator_value, indicator_type, source_id)
                VALUES (%s, 'IPv4', %s)
                RETURNING indicator_id
                """,
                ("192.0.2.240", source_id),
            )
            indicator_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO security_events
                    (event_type, player_id, source_ip)
                VALUES ('failed_login', 'E2E_PLAYER', %s)
                RETURNING event_id
                """,
                ("192.0.2.240",),
            )
            event_id = cursor.fetchone()[0]

        # 2. Verify correlation.
        matches = correlate_ip_indicators(conn)

        relevant = [
            m for m in matches
            if m["event_id"] == event_id
            and m["indicator_id"] == indicator_id
        ]

        assert len(relevant) == 1

        # 3. Generate one case.
        assert generate_cases(conn) == 1

        # Running again should not duplicate it.
        assert generate_cases(conn) == 0

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT case_id
                FROM automated_cases
                WHERE event_id = %s
                """,
                (event_id,),
            )

            case_id = cursor.fetchone()[0]

        evidence = get_case_evidence(case_id, conn)

        assert len(evidence) == 1

        # 4. Score the evidence.
        assessment = calculate_case_priority(evidence)

        assert assessment["score"] == 20
        assert assessment["priority"] == "Medium"

        # 5. Update case and add a note.
        assert update_case(
            case_id,
            "In Progress",
            "Medium",
            conn=conn,
            actor="E2E Test Analyst",
        )

        note_id = add_case_note(
            case_id,
            "E2E Test Analyst",
            "Reviewed synthetic security event.",
            conn,
        )

        assert note_id is not None

        # 6. Verify audit history.
        history = get_case_audit_history(case_id, conn)

        actions = {entry["action"] for entry in history}

        assert "case_updated" in actions
        assert "note_added" in actions

        # 7. Generate and verify investigation report.
        report = generate_case_report(case_id, conn)

        assert "192.0.2.240" in report
        assert "Reviewed synthetic security event." in report
        assert "In Progress" in report
        assert "Investigation Priority Analysis" in report
        assert "Audit History" in report

    finally:
        # Do not persist any test intelligence or cases.
        conn.rollback()
        conn.close()