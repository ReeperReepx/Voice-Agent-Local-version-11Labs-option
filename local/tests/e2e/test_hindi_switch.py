"""End-to-end test: Hindi explanation mode triggers and reverts."""

import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.api.http_gateway import app, session_manager


@pytest.fixture(autouse=True)
def reset():
    session_manager._sessions.clear()
    yield


@pytest.fixture
def client():
    return TestClient(app)


class TestHindiExplanationSwitch:
    """Test Hindi explanation mode in an English interview."""

    def test_explanation_mode_triggers(self, client):
        """Hindi explanation request triggers explanation mode."""
        start = client.post("/api/session/start", json={}).json()
        sid = start["session_id"]

        # Normal English answer
        result = client.post(f"/api/session/{sid}/answer", json={
            "question_id": 1,
            "answer": "My name is Preet and I want to study abroad",
            "category": "background",
        }).json()
        assert result["explanation_mode"] is False

        # Hindi explanation request
        result = client.post(f"/api/session/{sid}/answer", json={
            "question_id": 2,
            "answer": "Hindi mein samjha do please",
            "category": "academics",
        }).json()
        assert result["explanation_mode"] is True
        assert result["language_action"] == "switch_to_hindi"

    def test_explanation_mode_reverts(self, client):
        """After Hindi explanation, mode reverts to English."""
        start = client.post("/api/session/start", json={}).json()
        sid = start["session_id"]
        session = session_manager.get_session(sid)

        # Trigger explanation mode
        client.post(f"/api/session/{sid}/answer", json={
            "question_id": 1,
            "answer": "Can you explain this in Hindi?",
            "category": "academics",
        })

        # Auto revert
        session.language_controller.auto_revert()

        # Next answer should be normal English mode
        result = client.post(f"/api/session/{sid}/answer", json={
            "question_id": 2,
            "answer": "I have completed my Bachelor's degree in Computer Science",
            "category": "academics",
        }).json()
        assert result["explanation_mode"] is False
        assert result["language_action"] == "none"

    def test_switch_count_tracked(self, client):
        """Language switches are counted in the final report."""
        start = client.post("/api/session/start", json={}).json()
        sid = start["session_id"]
        session = session_manager.get_session(sid)

        # Trigger explanation mode twice
        client.post(f"/api/session/{sid}/answer", json={
            "question_id": 1,
            "answer": "Hindi mein samjha do",
            "category": "academics",
        })
        session.language_controller.auto_revert()

        client.post(f"/api/session/{sid}/answer", json={
            "question_id": 2,
            "answer": "Explain in Hindi please",
            "category": "finance",
        })
        session.language_controller.auto_revert()

        # End and check report
        report = client.post(f"/api/session/{sid}/end").json()
        assert report["language_switches"] == 2

    def test_english_interview_with_hindi_explanation(self, client):
        """Full flow: English interview → Hindi explanation → revert → continue English."""
        start = client.post(
            "/api/session/start",
            json={"destination_country": "US"},
        ).json()
        sid = start["session_id"]
        session = session_manager.get_session(sid)

        # Greeting (English)
        r1 = client.post(f"/api/session/{sid}/answer", json={
            "question_id": 1,
            "answer": "Good morning, my name is Preet Kumar from New Delhi",
            "category": "background",
        }).json()
        assert r1["explanation_mode"] is False

        # Advance to academics
        client.post(f"/api/session/{sid}/advance")

        # Request Hindi explanation
        r2 = client.post(f"/api/session/{sid}/answer", json={
            "question_id": 2,
            "answer": "Hindi mein samjha do, mujhe samajh nahi aaya",
            "category": "academics",
        }).json()
        assert r2["explanation_mode"] is True

        # Auto revert
        revert_msg = session.language_controller.auto_revert()
        assert "continue" in revert_msg.lower()

        # Continue in English
        r3 = client.post(f"/api/session/{sid}/answer", json={
            "question_id": 3,
            "answer": "I completed my BTech in Computer Science from DTU with 8.5 GPA",
            "category": "academics",
        }).json()
        assert r3["explanation_mode"] is False

        # End
        report = client.post(f"/api/session/{sid}/end").json()
        assert report["language_switches"] == 1
        assert report["total_questions"] >= 3
