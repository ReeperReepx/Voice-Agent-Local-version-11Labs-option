"""Integration tests for the API layer.

Tests HTTP endpoints and session lifecycle.
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.api.http_gateway import app, session_manager


@pytest.fixture(autouse=True)
def reset_sessions():
    """Reset session manager between tests."""
    session_manager._sessions.clear()
    yield


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "active_sessions" in data


class TestSessionEndpoints:
    def test_start_session(self, client):
        response = client.post(
            "/api/session/start",
            json={"destination_country": "US", "origin_country": "India"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["destination_country"] == "US"
        assert data["current_state"] == "greeting"

    def test_start_session_default_values(self, client):
        response = client.post("/api/session/start", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["destination_country"] == "US"

    def test_get_session(self, client):
        # Start
        start = client.post("/api/session/start", json={}).json()
        sid = start["session_id"]

        # Get
        response = client.get(f"/api/session/{sid}")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == sid
        assert data["is_active"] is True

    def test_get_session_not_found(self, client):
        response = client.get("/api/session/nonexistent")
        assert response.status_code == 404

    def test_log_message(self, client):
        start = client.post("/api/session/start", json={}).json()
        sid = start["session_id"]

        response = client.post(
            f"/api/session/{sid}/message",
            json={"role": "student", "text": "My name is Preet", "language": "en"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_process_answer(self, client):
        start = client.post("/api/session/start", json={}).json()
        sid = start["session_id"]

        response = client.post(
            f"/api/session/{sid}/answer",
            json={
                "question_id": 1,
                "answer": "I completed my Bachelor's in Computer Science from Delhi University with 85 percent marks",
                "category": "academics",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert data["score"] > 0
        assert "language_action" in data
        assert "contradictions" in data

    def test_advance_state(self, client):
        start = client.post("/api/session/start", json={}).json()
        sid = start["session_id"]

        response = client.post(f"/api/session/{sid}/advance")
        assert response.status_code == 200
        assert response.json()["new_state"] == "academics"

    def test_end_session(self, client):
        start = client.post("/api/session/start", json={}).json()
        sid = start["session_id"]

        response = client.post(f"/api/session/{sid}/end")
        assert response.status_code == 200
        data = response.json()
        assert "average_score" in data
        assert "readiness" in data
        assert data["session_id"] == sid

    def test_end_session_not_found(self, client):
        response = client.post("/api/session/nonexistent/end")
        assert response.status_code == 404

    def test_full_session_lifecycle(self, client):
        """Test complete session: start → messages → advance → end."""
        # Start
        start = client.post(
            "/api/session/start",
            json={"destination_country": "UK"},
        ).json()
        sid = start["session_id"]

        # Log message
        client.post(
            f"/api/session/{sid}/message",
            json={"role": "student", "text": "Hello, my name is Preet"},
        )

        # Process answer
        client.post(
            f"/api/session/{sid}/answer",
            json={"question_id": 1, "answer": "My name is Preet", "category": "background"},
        )

        # Advance
        adv = client.post(f"/api/session/{sid}/advance").json()
        assert adv["new_state"] == "academics"

        # End
        report = client.post(f"/api/session/{sid}/end").json()
        assert report["total_questions"] >= 0
        assert "readiness" in report


class TestQuestionEndpoints:
    def test_get_questions(self, client):
        response = client.get("/api/questions/US")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] > 0
        assert len(data["questions"]) > 0

    def test_get_questions_with_category(self, client):
        response = client.get("/api/questions/US?category=finance")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] > 0
        assert all(q["category"] == "finance" for q in data["questions"])

    def test_get_questions_invalid_country(self, client):
        response = client.get("/api/questions/XX")
        assert response.status_code == 400

    def test_get_destinations(self, client):
        response = client.get("/api/destinations")
        assert response.status_code == 200
        data = response.json()
        assert len(data["destinations"]) == 20

    def test_get_risk_factors(self, client):
        response = client.get("/api/risk/US?origin=India")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] > 0
