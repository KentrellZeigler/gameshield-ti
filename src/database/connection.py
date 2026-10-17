
import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    database_url = os.getenv(
        "DATABASE_URL",
        "dbname=gameshield_ti"
    )

    return psycopg.connect(database_url)

def get_test_connection():
    """
    Open the dedicated GameShield test database.

    Refuse to proceed if the active database
    is not gameshield_ti_test.
    """

    conn = psycopg.connect(
        "dbname=gameshield_ti_test"
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database()")
            database_name = cursor.fetchone()[0]

        if database_name != "gameshield_ti_test":
            raise RuntimeError(
                "Tests must use gameshield_ti_test."
            )

        return conn

    except Exception:
        conn.close()
        raise
