import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from arviva_agent.api.main import app


def test_run_contract_shape_and_400() -> None:
    client = TestClient(app)

    ok_response = client.post("/api/agent/run", json={"goal": "Automatisera deployment", "max_iterations": 5})
    assert ok_response.status_code == 200
    ok_payload = ok_response.json()
    assert set(ok_payload.keys()) == {"status", "details"}

    bad_response = client.post("/api/agent/run", json={"goal": ""})
    assert bad_response.status_code == 400
