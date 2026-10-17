
import psycopg

from src.analyzers.case_generator import (
    generate_cases,
    get_automated_cases,
)


def test_case_generation():
    conn = psycopg.connect(
        "dbname=gameshield_ti_test"
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database()")
            assert cursor.fetchone()[0] == "gameshield_ti_test"

            cursor.execute(
                """
                INSERT INTO intelligence_sources
                    (source_name)
                VALUES ('Case Generator Test')
                RETURNING source_id
                """
            )
            source_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO threat_indicators
                    (indicator_value, indicator_type, source_id)
                VALUES (%s, 'IPv4', %s)
                """,
                ("192.0.2.99", source_id),
            )

            cursor.execute(
                """
                INSERT INTO security_events
                    (event_type, player_id, source_ip)
                VALUES ('failed_login', 'TEST_CASE_PLAYER', %s)
                """,
                ("192.0.2.99",),
            )

        first_run = generate_cases(conn)
        second_run = generate_cases(conn)

        assert first_run == 1
        assert second_run == 0

        cases = get_automated_cases(conn)

        assert len(cases) == 1
        assert cases[0]["priority"] == "Medium"
        assert cases[0]["source_ip"] == "192.0.2.99"

    finally:
        conn.rollback()
        conn.close()
