import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from arviva_agent.api.main import app


def test_run_endpoint_exists() -> None:
    client = TestClient(app)
    response = client.post("/api/agent/run", json={"goal": "Test goal", "max_iterations": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"success", "incomplete", "needs_replan", "failed"}
    assert "details" in data


def test_run_endpoint_returns_400_for_invalid_body() -> None:
    client = TestClient(app)
    response = client.post("/api/agent/run", json={"goal": ""})
    assert response.status_code == 400


def test_status_endpoint_exists() -> None:
    client = TestClient(app)
    response = client.get("/api/agent/status")
    assert response.status_code == 200
    data = response.json()
    assert "agent_s" in data
    assert "superagi" in data
    assert "reachable" in data["agent_s"]
    assert "mode" in data["agent_s"]
    assert "reachable" in data["superagi"]
    assert "mode" in data["superagi"]
    assert "url" in data["superagi"]
