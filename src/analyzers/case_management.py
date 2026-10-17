
from contextlib import nullcontext

from psycopg.rows import dict_row

from src.database.connection import get_connection


VALID_STATUSES = {
    "Open",
    "In Progress",
    "Closed",
}

VALID_PRIORITIES = {
    "Low",
    "Medium",
    "High",
    "Critical",
}


def update_case(case_id, status, priority, conn=None):
    """Update the status and assigned priority of a case."""

    if status not in VALID_STATUSES:
        raise ValueError("Invalid investigation status.")

    if priority not in VALID_PRIORITIES:
        raise ValueError("Invalid investigation priority.")

    context = (
        nullcontext(conn)
        if conn is not None
        else get_connection()
    )

    with context as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE automated_cases
                SET status = %s,
                    priority = %s
                WHERE case_id = %s
                RETURNING case_id
                """,
                (status, priority, case_id),
            )

            updated = cursor.fetchone() is not None

        if conn is None:
            connection.commit()

    return updated


def add_case_note(case_id, author, note_text, conn=None):
    """Save an investigator's note to a case."""

    author = author.strip()
    note_text = note_text.strip()

    if not author:
        raise ValueError("Author cannot be empty.")

    if not note_text:
        raise ValueError("Investigation note cannot be empty.")

    if len(author) > 100:
        raise ValueError("Author name is too long.")

    context = (
        nullcontext(conn)
        if conn is not None
        else get_connection()
    )

    with context as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO case_notes
                    (case_id, author, note_text)
                VALUES (%s, %s, %s)
                RETURNING note_id
                """,
                (case_id, author, note_text),
            )

            note_id = cursor.fetchone()[0]

        if conn is None:
            connection.commit()

    return note_id


def get_case_notes(case_id, conn=None):
    """Retrieve notes for a selected investigation."""

    context = (
        nullcontext(conn)
        if conn is not None
        else get_connection()
    )

    with context as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    note_id,
                    case_id,
                    author,
                    note_text,
                    created_at
                FROM case_notes
                WHERE case_id = %s
                ORDER BY created_at DESC, note_id DESC
                """,
                (case_id,),
            )

            return cursor.fetchall()
