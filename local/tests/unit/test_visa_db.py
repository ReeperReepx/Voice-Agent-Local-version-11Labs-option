"""Unit tests for visa database: schema, seed data, and retrieval."""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.visa_db.retrieval import (
    VALID_CATEGORIES,
    VALID_COUNTRIES,
    get_connection,
    get_destinations,
    get_followups,
    get_question_by_id,
    get_questions_by_country,
    get_questions_progressive,
    get_risk_factors,
    init_db,
    seed_db,
)


@pytest.fixture
def db_path():
    """Create a fresh test database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    init_db(path)
    seed_db(path)
    yield path
    os.unlink(path)


class TestSchemaCreation:
    """Test that schema creates without error."""

    def test_schema_creates_successfully(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            path = f.name
        try:
            init_db(path)
            conn = get_connection(path)
            # Verify tables exist
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            table_names = {t["name"] for t in tables}
            assert "destinations" in table_names
            assert "visa_questions" in table_names
            assert "followups" in table_names
            assert "risk_factors" in table_names
            conn.close()
        finally:
            os.unlink(path)

    def test_schema_is_idempotent(self):
        """Schema can be applied twice without error."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            path = f.name
        try:
            init_db(path)
            init_db(path)  # Second call should not fail
        finally:
            os.unlink(path)


class TestSeedData:
    """Test that seed data loads correctly."""

    def test_all_20_destinations_loaded(self, db_path):
        destinations = get_destinations(db_path)
        assert len(destinations) == 20

    def test_destination_countries_match(self, db_path):
        destinations = get_destinations(db_path)
        codes = {d["country_code"] for d in destinations}
        assert codes == set(VALID_COUNTRIES)

    def test_questions_exist_for_all_countries(self, db_path):
        for code in VALID_COUNTRIES:
            questions = get_questions_by_country(code, db_path=db_path)
            assert len(questions) > 0, f"No questions found for {code}"

    def test_us_has_questions_in_all_categories(self, db_path):
        for category in VALID_CATEGORIES:
            questions = get_questions_by_country("US", category=category, db_path=db_path)
            assert len(questions) > 0, f"No US questions in category: {category}"

    def test_uk_has_questions(self, db_path):
        questions = get_questions_by_country("UK", db_path=db_path)
        assert len(questions) >= 8

    def test_followups_exist(self, db_path):
        # US question 1 should have a followup
        followups = get_followups(1, db_path=db_path)
        assert len(followups) > 0

    def test_risk_factors_for_us_india(self, db_path):
        risks = get_risk_factors("US", origin_country="India", db_path=db_path)
        assert len(risks) > 0
        assert risks[0]["scrutiny_level"] >= 2


class TestRetrieval:
    """Test retrieval functions."""

    def test_get_questions_by_country_us(self, db_path):
        questions = get_questions_by_country("US", db_path=db_path)
        assert len(questions) >= 10
        assert all(q["destination_country"] == "US" for q in questions)

    def test_get_questions_by_category(self, db_path):
        questions = get_questions_by_country("US", category="finance", db_path=db_path)
        assert len(questions) >= 2
        assert all(q["category"] == "finance" for q in questions)

    def test_get_questions_by_difficulty(self, db_path):
        easy = get_questions_by_country("US", difficulty=1, db_path=db_path)
        hard = get_questions_by_country("US", difficulty=3, db_path=db_path)
        assert len(easy) > 0
        assert len(hard) > 0
        assert all(q["difficulty_level"] == 1 for q in easy)
        assert all(q["difficulty_level"] == 3 for q in hard)

    def test_get_questions_by_country_and_category_and_difficulty(self, db_path):
        questions = get_questions_by_country(
            "US", category="intent", difficulty=3, db_path=db_path
        )
        assert len(questions) > 0
        assert all(
            q["category"] == "intent" and q["difficulty_level"] == 3
            for q in questions
        )

    def test_progressive_ordering(self, db_path):
        questions = get_questions_progressive("US", db_path=db_path)
        difficulties = [q["difficulty_level"] for q in questions]
        # Should be sorted: all 1s, then 2s, then 3s
        assert difficulties == sorted(difficulties)

    def test_get_question_by_id(self, db_path):
        question = get_question_by_id(1, db_path=db_path)
        assert question is not None
        assert question["id"] == 1

    def test_get_question_by_id_not_found(self, db_path):
        question = get_question_by_id(99999, db_path=db_path)
        assert question is None

    def test_invalid_country_raises(self, db_path):
        with pytest.raises(ValueError, match="Unsupported country"):
            get_questions_by_country("XX", db_path=db_path)

    def test_invalid_category_raises(self, db_path):
        with pytest.raises(ValueError, match="Invalid category"):
            get_questions_by_country("US", category="invalid", db_path=db_path)

    def test_invalid_difficulty_raises(self, db_path):
        with pytest.raises(ValueError, match="Invalid difficulty"):
            get_questions_by_country("US", difficulty=5, db_path=db_path)

    def test_get_followups(self, db_path):
        followups = get_followups(1, db_path=db_path)
        assert isinstance(followups, list)
        for f in followups:
            assert f["parent_question_id"] == 1

    def test_risk_factors_all_destinations(self, db_path):
        risks = get_risk_factors("US", db_path=db_path)
        assert len(risks) > 0

    def test_risk_factors_by_origin(self, db_path):
        risks = get_risk_factors("UK", origin_country="India", db_path=db_path)
        assert len(risks) > 0

    def test_risk_factors_invalid_country(self, db_path):
        with pytest.raises(ValueError):
            get_risk_factors("XX", db_path=db_path)

    def test_questions_have_hindi_text(self, db_path):
        """At least some questions should have Hindi translations."""
        questions = get_questions_by_country("US", db_path=db_path)
        hindi_count = sum(1 for q in questions if q.get("question_text_hi"))
        assert hindi_count > 0

    def test_questions_have_officer_objective(self, db_path):
        questions = get_questions_by_country("US", db_path=db_path)
        for q in questions:
            assert q["officer_objective"], f"Question {q['id']} missing officer_objective"
