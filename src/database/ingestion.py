
from src.database.connection import get_connection


def save_indicators(indicators):
    """
    Save validated OTX indicators into PostgreSQL.

    Returns the number of newly inserted records.
    """

    if not indicators:
        return 0

    inserted_count = 0

    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO intelligence_sources
                    (source_name, source_url)
                VALUES (%s, %s)
                ON CONFLICT (source_name)
                DO UPDATE SET
                    source_url = EXCLUDED.source_url
                RETURNING source_id
                """,
                (
                    "AlienVault OTX",
                    "https://otx.alienvault.com/",
                ),
            )

            source_id = cursor.fetchone()[0]

            for indicator in indicators:
                cursor.execute(
                    """
                    INSERT INTO threat_indicators
                        (
                            indicator_value,
                            indicator_type,
                            source_id,
                            confidence,
                            description
                        )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT
                        (indicator_type, indicator_value, source_id)
                    DO NOTHING
                    RETURNING indicator_id
                    """,
                    (
                        indicator["indicator_value"],
                        indicator["indicator_type"],
                        source_id,
                        None,
                        f"OTX pulse: {indicator['pulse_name']}",
                    ),
                )

                if cursor.fetchone() is not None:
                    inserted_count += 1

    return inserted_count
