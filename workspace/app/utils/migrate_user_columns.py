from __future__ import annotations

from sqlalchemy import text

from app import db


def migrate_user_columns() -> None:
    """SQLite-only: add missing columns to the existing users table.

    This project currently uses SQLite without Alembic migrations.
    """

    # Only safe for SQLite; other DBs should use proper migrations.
    if db.engine.dialect.name != "sqlite":
        return

    existing_cols = {
        row["name"]
        for row in db.session.execute(text("PRAGMA table_info(users)")).mappings()
    }

    additions: dict[str, str] = {
        "award_amount": "TEXT",
        "scholarship_category": "TEXT",
        "state": "TEXT",
        "other_circumstances": "TEXT",
    }

    for col, col_type in additions.items():
        if col in existing_cols:
            continue
        db.session.execute(text(f"ALTER TABLE users ADD COLUMN {col} {col_type}"))

    db.session.commit()
