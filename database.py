import sqlite3
from datetime import date
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / "campuswell.db"


def connect():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS moods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_date TEXT NOT NULL UNIQUE,
                mood_score INTEGER NOT NULL
                    CHECK (mood_score BETWEEN 1 AND 5),
                note TEXT NOT NULL DEFAULT ''
            )
            """
        )


def get_moods():
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT id, entry_date, mood_score, note
            FROM moods
            ORDER BY entry_date ASC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def save_mood(entry_date, score, note):
    if type(score) is not int or score not in range(1, 6):
        return False, "Choose a mood from 1 to 5."

    if not isinstance(note, str) or len(note) > 500:
        return False, "Notes must be 500 characters or fewer."

    if not isinstance(entry_date, str):
        return False, "Choose a valid date."

    try:
        parsed = date.fromisoformat(entry_date)

        if parsed.isoformat() != entry_date:
            raise ValueError

        if parsed > date.today():
            return False, "Choose today or an earlier date."

    except ValueError:
        return False, "Choose a valid date."

    with connect() as connection:
        connection.execute(
            """
            INSERT INTO moods (entry_date, mood_score, note)
            VALUES (?, ?, ?)
            ON CONFLICT(entry_date)
            DO UPDATE SET
                mood_score = excluded.mood_score,
                note = excluded.note
            """,
            (entry_date, score, note.strip()),
        )

    return True, "Mood saved."


def clear_moods():
    with connect() as connection:
        connection.execute("DELETE FROM moods")
