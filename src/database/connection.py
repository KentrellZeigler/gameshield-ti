
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
