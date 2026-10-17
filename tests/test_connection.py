
from src.database.connection import get_connection


def test_database_connection():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database()")
            result = cursor.fetchone()

    assert result[0] == "gameshield_ti"
