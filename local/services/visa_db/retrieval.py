"""Visa question database retrieval layer.

Provides query functions for questions by country, category, and difficulty.
Uses SQLite for local development and can connect to PostgreSQL in production.
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = os.getenv("VISA_DB_PATH", str(Path(__file__).parent / "visa.db"))

VALID_COUNTRIES = [
    "US", "UK", "CA", "AU", "DE", "FR", "NL", "IE", "IT", "ES",
    "CH", "SE", "FI", "NO", "DK", "JP", "KR", "SG", "NZ", "AE",
]

VALID_CATEGORIES = [
    "academics", "finance", "intent", "ties", "background",
    "course_choice", "country_specific",
]


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Get a database connection."""
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize the database schema from schema.sql."""
    schema_path = Path(__file__).parent / "schema.sql"
    conn = get_connection(db_path)
    try:
        # Adapt PostgreSQL schema for SQLite
        schema = schema_path.read_text()
        # SQLite adaptations
        schema = schema.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
        schema = schema.replace("VARCHAR(3)", "TEXT")
        schema = schema.replace("VARCHAR(50)", "TEXT")
        schema = schema.replace("VARCHAR(100)", "TEXT")
        # Remove CHECK constraints that reference specific values (SQLite handles these)
        # Remove ON CONFLICT for compatibility
        schema = schema.replace("ON CONFLICT (country_code) DO NOTHING", "")
        # Remove IF NOT EXISTS from INDEX (older SQLite compat)
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()


def seed_db(db_path: Optional[str] = None) -> None:
    """Load seed data into the database."""
    seed_dir = Path(__file__).parent / "seed"
    conn = get_connection(db_path)
    try:
        for seed_file in ["destinations.sql", "questions.sql", "followups.sql", "risk_factors.sql"]:
            path = seed_dir / seed_file
            if path.exists():
                sql = path.read_text()
                # Adapt for SQLite: INSERT OR IGNORE instead of ON CONFLICT
                sql = sql.replace("INSERT INTO", "INSERT OR IGNORE INTO")
                sql = sql.replace("ON CONFLICT (country_code) DO NOTHING", "")
                try:
                    conn.executescript(sql)
                except sqlite3.IntegrityError:
                    pass  # Skip duplicates on re-seed
        conn.commit()
    finally:
        conn.close()


def get_destinations(db_path: Optional[str] = None) -> list[dict]:
    """Return all supported destination countries."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute("SELECT * FROM destinations ORDER BY country_name").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_questions_by_country(
    country_code: str,
    category: Optional[str] = None,
    difficulty: Optional[int] = None,
    db_path: Optional[str] = None,
) -> list[dict]:
    """Retrieve questions for a specific destination country.

    Args:
        country_code: ISO country code (e.g., 'US', 'UK')
        category: Optional filter by category
        difficulty: Optional filter by difficulty level (1-3)
        db_path: Optional database path override
    """
    if country_code not in VALID_COUNTRIES:
        raise ValueError(f"Unsupported country: {country_code}. Must be one of {VALID_COUNTRIES}")

    conn = get_connection(db_path)
    try:
        query = "SELECT * FROM visa_questions WHERE destination_country = ?"
        params: list = [country_code]

        if category:
            if category not in VALID_CATEGORIES:
                raise ValueError(f"Invalid category: {category}. Must be one of {VALID_CATEGORIES}")
            query += " AND category = ?"
            params.append(category)

        if difficulty is not None:
            if difficulty not in (1, 2, 3):
                raise ValueError(f"Invalid difficulty: {difficulty}. Must be 1, 2, or 3")
            query += " AND difficulty_level = ?"
            params.append(difficulty)

        query += " ORDER BY difficulty_level, id"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_followups(question_id: int, db_path: Optional[str] = None) -> list[dict]:
    """Get follow-up questions for a given parent question."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM followups WHERE parent_question_id = ?",
            (question_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_risk_factors(
    destination_country: str,
    origin_country: Optional[str] = None,
    db_path: Optional[str] = None,
) -> list[dict]:
    """Get risk factors for a destination (optionally filtered by origin)."""
    if destination_country not in VALID_COUNTRIES:
        raise ValueError(f"Unsupported country: {destination_country}")

    conn = get_connection(db_path)
    try:
        query = "SELECT * FROM risk_factors WHERE destination_country = ?"
        params: list = [destination_country]

        if origin_country:
            query += " AND origin_country = ?"
            params.append(origin_country)

        query += " ORDER BY scrutiny_level DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_question_by_id(question_id: int, db_path: Optional[str] = None) -> Optional[dict]:
    """Get a single question by its ID."""
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT * FROM visa_questions WHERE id = ?", (question_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_questions_progressive(
    country_code: str,
    db_path: Optional[str] = None,
) -> list[dict]:
    """Get questions ordered easy → moderate → advanced for progressive interview flow."""
    return get_questions_by_country(country_code, db_path=db_path)
