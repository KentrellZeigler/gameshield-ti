
import os

import psycopg
import pytest

from src.analyzers.correlation import correlate_ip_indicators


@pytest.fixture
def test_db():
    """Use the isolated test database for each test."""

    with psycopg.connect(
        "dbname=gameshield_ti_test"
    ) as conn:

        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database()")
            database_name = cursor.fetchone()[0]

        if database_name != "gameshield_ti_test":
            raise RuntimeError("Unsafe test database!")

        yield conn

        # Undo all test inserts.
        conn.rollback()


def add_indicator(conn, ip, indicator_type="IPv4"):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO intelligence_sources
                (source_name)
            VALUES ('Test Intelligence Source')
            ON CONFLICT (source_name)
            DO UPDATE SET
                source_name = EXCLUDED.source_name
            RETURNING source_id
            """
        )

        source_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO threat_indicators
                (indicator_value, indicator_type, source_id)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (ip, indicator_type, source_id),
        )


def add_event(conn, ip):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO security_events
                (event_type, player_id, source_ip)
            VALUES ('failed_login', 'TEST_PLAYER', %s)
            """,
            (ip,),
        )


def test_matching_ipv4(test_db):
    add_indicator(test_db, "192.0.2.10")
    add_event(test_db, "192.0.2.10")

    matches = correlate_ip_indicators(test_db)

    assert len(matches) == 1
    assert matches[0]["source_ip"] == "192.0.2.10"


def test_unmatched_ip(test_db):
    add_indicator(test_db, "192.0.2.10")
    add_event(test_db, "198.51.100.25")

    matches = correlate_ip_indicators(test_db)

    assert len(matches) == 0


def test_matching_ipv6(test_db):
    add_indicator(
        test_db, "2001:db8::10", indicator_type="IPv6"
    )
    add_event(test_db, "2001:db8::10")

    matches = correlate_ip_indicators(test_db)

    assert len(matches) == 1
    assert matches[0]["source_ip"] == "2001:db8::10"


def test_wrong_indicator_type(test_db):
    add_indicator(
        test_db, "192.0.2.10", indicator_type="domain"
    )
    add_event(test_db, "192.0.2.10")

    matches = correlate_ip_indicators(test_db)

    assert len(matches) == 0


def test_duplicate_indicator_prevention(test_db):
    add_indicator(test_db, "192.0.2.10")
    add_indicator(test_db, "192.0.2.10")
    add_event(test_db, "192.0.2.10")

    matches = correlate_ip_indicators(test_db)

    assert len(matches) == 1
