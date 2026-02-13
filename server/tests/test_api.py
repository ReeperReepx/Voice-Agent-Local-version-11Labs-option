"""Tests for the FastAPI endpoints."""

from unittest.mock import patch
from fastapi.testclient import TestClient

from server.app import app

client = TestClient(app)


def test_root_serves_html():
    response = client.get("/")
    assert response.status_code == 200


@patch("server.app.get_signed_url")
def test_start_session_with_signed_url(mock_signed_url):
    mock_signed_url.return_value = "wss://fake-signed-url"
    response = client.post("/api/session/start")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "agent_id" in data
    assert data["signed_url"] == "wss://fake-signed-url"
    assert "system_prompt" in data


@patch("server.app.get_signed_url", side_effect=Exception("401"))
def test_start_session_falls_back_to_agent_id(mock_signed_url):
    response = client.post("/api/session/start")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "agent_id" in data
    assert data["signed_url"] is None


def test_get_nonexistent_session():
    response = client.get("/api/session/nonexistent")
    assert response.status_code == 404


@patch("server.app.get_signed_url", side_effect=Exception("skip"))
def test_end_session_returns_feedback(mock_signed_url):
    start_res = client.post("/api/session/start")
    session_id = start_res.json()["session_id"]
    end_res = client.post(f"/api/session/{session_id}/end")
    assert end_res.status_code == 200
    data = end_res.json()
    assert "summary" in data
    assert "english_proficiency" in data
    assert "language_switches" in data


def test_end_nonexistent_session():
    response = client.post("/api/session/nonexistent/end")
    assert response.status_code == 404
