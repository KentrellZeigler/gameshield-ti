
from contextlib import nullcontext

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

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


def update_case(
    case_id,
    status,
    priority,
    conn=None,
    actor="Local Analyst",
):
    """Update a case and record its change atomically."""

    if status not in VALID_STATUSES:
        raise ValueError("Invalid investigation status.")

    if priority not in VALID_PRIORITIES:
        raise ValueError("Invalid investigation priority.")

    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("Actor cannot be empty.")

    actor = actor.strip()

    if len(actor) > 100:
        raise ValueError("Actor label is too long.")

    context = (
        nullcontext(conn)
        if conn is not None
        else get_connection()
    )

    with context as connection:
        with connection.cursor(row_factory=dict_row) as cursor:

            cursor.execute(
                """
                SELECT status, priority
                FROM automated_cases
                WHERE case_id = %s
                FOR UPDATE
                """,
                (case_id,),
            )

            previous = cursor.fetchone()

            if previous is None:
                return False

            old_values = {
                "status": previous["status"],
                "priority": previous["priority"],
            }

            new_values = {
                "status": status,
                "priority": priority,
            }

            # Do not log changes that didn't happen.
            if old_values == new_values:
                return True

            cursor.execute(
                """
                UPDATE automated_cases
                SET status = %s,
                    priority = %s
                WHERE case_id = %s
                """,
                (status, priority, case_id),
            )

            cursor.execute(
                """
                INSERT INTO case_audit_log
                    (case_id, action, actor,
                     old_value, new_value)
                VALUES (
                    %s, 'case_updated', %s, %s, %s
                )
                """,
                (
                    case_id,
                    actor,
                    Jsonb(old_values),
                    Jsonb(new_values),
                ),
            )

        if conn is None:
            connection.commit()

    return True


def add_case_note(case_id, author, note_text, conn=None):
    """Insert a note and its audit entry atomically."""

    if not isinstance(author, str):
        raise ValueError("Author must be text.")

    if not isinstance(note_text, str):
        raise ValueError("Note must be text.")

    author = author.strip()
    note_text = note_text.strip()

    if not author:
        raise ValueError("Author cannot be empty.")

    if len(author) > 100:
        raise ValueError("Author name is too long.")

    if not note_text:
        raise ValueError("Investigation note cannot be empty.")

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

            cursor.execute(
                """
                INSERT INTO case_audit_log
                    (case_id, action, actor,
                     old_value, new_value)
                VALUES (
                    %s, 'note_added', %s, NULL, %s
                )
                """,
                (
                    case_id,
                    author,
                    Jsonb({"note_id": note_id}),
                ),
            )

        if conn is None:
            connection.commit()

    return note_id


def get_case_notes(case_id, conn=None):
    """Retrieve notes belonging to a case."""

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


def get_case_audit_history(case_id, conn=None):
    """Return recorded case activity, newest first."""

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
                    audit_id,
                    case_id,
                    action,
                    actor,
                    old_value,
                    new_value,
                    created_at
                FROM case_audit_log
                WHERE case_id = %s
                ORDER BY created_at DESC, audit_id DESC
                """,
                (case_id,),
            )

            return cursor.fetchall()
