"""End-to-end test: full English interview completes (simulated)."""

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


class TestFullEnglishInterview:
    """Simulate a complete English interview session through the API."""

    def test_full_interview_us(self, client):
        """Full English interview for US completes with valid report."""
        # 1. Start session
        start = client.post(
            "/api/session/start",
            json={"destination_country": "US", "origin_country": "India"},
        ).json()
        sid = start["session_id"]
        assert start["current_state"] == "greeting"

        # 2. Greeting phase
        client.post(f"/api/session/{sid}/message", json={
            "role": "student", "text": "Good morning. My name is Preet Kumar.", "language": "en",
        })
        client.post(f"/api/session/{sid}/answer", json={
            "question_id": 1, "answer": "My name is Preet Kumar and I want to study in the United States.",
            "category": "background",
        })

        # Advance to academics
        adv = client.post(f"/api/session/{sid}/advance").json()
        assert adv["new_state"] == "academics"

        # 3. Academics phase
        client.post(f"/api/session/{sid}/answer", json={
            "question_id": 2,
            "answer": "I completed my Bachelor of Technology in Computer Science from Delhi Technological University with a GPA of 8.5 out of 10.",
            "category": "academics",
        })
        adv = client.post(f"/api/session/{sid}/advance").json()
        assert adv["new_state"] == "course_choice"

        # 4. Course choice
        client.post(f"/api/session/{sid}/answer", json={
            "question_id": 3,
            "answer": "I chose Stanford University because of their excellent AI research program led by Professor Andrew Ng. The curriculum includes machine learning and natural language processing courses that align with my research interests.",
            "category": "course_choice",
        })
        adv = client.post(f"/api/session/{sid}/advance").json()
        assert adv["new_state"] == "finance"

        # 5. Finance
        client.post(f"/api/session/{sid}/answer", json={
            "question_id": 4,
            "answer": "My father, who is a senior engineer at Tata Consultancy Services, is my financial sponsor. His annual income is 25 lakh rupees and we have 60 lakhs in savings. I also have an education loan approved from State Bank of India.",
            "category": "finance",
        })
        adv = client.post(f"/api/session/{sid}/advance").json()
        assert adv["new_state"] == "intent"

        # 6. Intent
        client.post(f"/api/session/{sid}/answer", json={
            "question_id": 5,
            "answer": "After completing my Masters, I plan to return to India and join my father's consulting business. I also have a job offer from Infosys waiting for me. My family is in Delhi and I want to be close to them.",
            "category": "intent",
        })
        adv = client.post(f"/api/session/{sid}/advance").json()
        assert adv["new_state"] == "country_specific"

        # 7. Country specific
        client.post(f"/api/session/{sid}/answer", json={
            "question_id": 6,
            "answer": "Yes, I have visited the US once before on a tourist visa for two weeks and returned on time. I have no family members in the US.",
            "category": "country_specific",
        })
        adv = client.post(f"/api/session/{sid}/advance").json()
        assert adv["new_state"] == "summary"

        # 8. End session
        report = client.post(f"/api/session/{sid}/end").json()

        # Verify report
        assert report["session_id"] == sid
        assert report["total_questions"] >= 6
        assert "readiness" in report
        assert "average_score" in report
        assert report["average_score"] > 0
        assert "duration_minutes" in report
        assert "language_switches" in report
        assert report["language_switches"] == 0  # English only

    def test_full_interview_uk(self, client):
        """Full English interview for UK."""
        start = client.post(
            "/api/session/start",
            json={"destination_country": "UK"},
        ).json()
        sid = start["session_id"]

        # Quick run through all states
        answers = [
            ("Hello, I am Preet.", "background"),
            ("I have a Bachelor's in Computer Science from Delhi University.", "academics"),
            ("I chose UCL because of their data science program.", "course_choice"),
            ("My parents are funding my education with savings of 30 lakh rupees.", "finance"),
            ("I will return to India to work at my family business.", "intent"),
            ("My IELTS score is 7.5 overall.", "country_specific"),
        ]

        for i, (answer, category) in enumerate(answers):
            client.post(f"/api/session/{sid}/answer", json={
                "question_id": i + 1, "answer": answer, "category": category,
            })
            if i < len(answers) - 1:
                client.post(f"/api/session/{sid}/advance")

        # Advance to summary
        client.post(f"/api/session/{sid}/advance")

        report = client.post(f"/api/session/{sid}/end").json()
        assert report["total_questions"] >= 6
        assert "readiness" in report

    def test_session_tracks_state_progression(self, client):
        """Verify states progress in order."""
        start = client.post("/api/session/start", json={}).json()
        sid = start["session_id"]

        expected_states = [
            "academics", "course_choice", "finance",
            "intent", "country_specific", "summary",
        ]

        for expected in expected_states:
            result = client.post(f"/api/session/{sid}/advance").json()
            assert result["new_state"] == expected

        # Cannot advance past summary → ended
        result = client.post(f"/api/session/{sid}/advance").json()
        assert result["new_state"] == "ended"

        # Cannot advance further
        result = client.post(f"/api/session/{sid}/advance")
        assert result.status_code == 400
