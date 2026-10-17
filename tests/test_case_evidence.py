
import psycopg

from src.analyzers.case_generator import (
    generate_cases,
    get_automated_cases,
    get_case_evidence,
)


def test_multiple_sources_single_case():
    conn = psycopg.connect("dbname=gameshield_ti_test")

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database()")

            assert cursor.fetchone()[0] == "gameshield_ti_test"

            for source in ["Test Source A", "Test Source B"]:
                cursor.execute(
                    """
                    INSERT INTO intelligence_sources (source_name)
                    VALUES (%s)
                    ON CONFLICT (source_name)
                    DO UPDATE SET source_name = EXCLUDED.source_name
                    RETURNING source_id
                    """,
                    (source,),
                )

                source_id = cursor.fetchone()[0]

                cursor.execute(
                    """
                    INSERT INTO threat_indicators
                        (indicator_value, indicator_type, source_id)
                    VALUES (%s, 'IPv4', %s)
                    ON CONFLICT
                        (indicator_type, indicator_value, source_id)
                    DO NOTHING
                    """,
                    ("192.0.2.199", source_id),
                )

            cursor.execute(
                """
                INSERT INTO security_events
                    (event_type, player_id, source_ip)
                VALUES ('failed_login', 'EVIDENCE_TEST', %s)
                RETURNING event_id
                """,
                ("192.0.2.199",),
            )

            event_id = cursor.fetchone()[0]

        # First run creates one case.
        assert generate_cases(conn) == 1

        # Second run must not create another case.
        assert generate_cases(conn) == 0

        cases = get_automated_cases(conn)

        matching_cases = [
            case for case in cases
            if case["player_id"] == "EVIDENCE_TEST"
            and case["source_ip"] == "192.0.2.199"
        ]

        assert len(matching_cases) == 1

        case_id = matching_cases[0]["case_id"]

        evidence = get_case_evidence(case_id, conn)

        # One case, two independently sourced indicators.
        assert len(evidence) == 2

        sources = {
            item["source_name"] for item in evidence
        }

        assert sources == {"Test Source A", "Test Source B"}

    finally:
        conn.rollback()
        conn.close()
