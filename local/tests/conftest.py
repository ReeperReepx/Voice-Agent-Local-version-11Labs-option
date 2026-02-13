"""Shared test fixtures for VisaWire Local tests."""

import os
import sys
import tempfile

import pytest

# Add local/ to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    from services.visa_db.retrieval import init_db, seed_db

    init_db(db_path)
    seed_db(db_path)
    yield db_path

    os.unlink(db_path)
