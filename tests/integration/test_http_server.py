"""Integration tests for HTTP server."""
import pytest
from fastapi.testclient import TestClient
from pikaclaw.server.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_status_endpoint(client):
    r = client.get("/status")
    assert r.status_code == 200
    data = r.json()
    assert "agent" in data
    assert "turns" in data
    assert "tokens" in data
    assert "cost" in data
    assert "session_id" in data


def test_agents_endpoint(client):
    r = client.get("/agents")
    assert r.status_code == 200
    agents = r.json()
    assert isinstance(agents, list)
    assert len(agents) == 9
    names = [a["name"] for a in agents]
    assert "build" in names
    assert "plan" in names
    assert "review" in names


def test_agents_have_required_fields(client):
    r = client.get("/agents")
    agents = r.json()
    for agent in agents:
        assert "name" in agent
        assert "display_name" in agent
        assert "icon" in agent
        assert "description" in agent
        assert "mode" in agent


def test_models_endpoint(client):
    r = client.get("/models")
    assert r.status_code == 200
    models = r.json()
    assert isinstance(models, list)
    assert len(models) > 0


def test_switch_agent(client):
    r = client.post("/agents/switch", json={"name": "plan"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["agent"] == "plan"


def test_switch_unknown_agent(client):
    r = client.post("/agents/switch", json={"name": "nonexistent"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "error"


def test_interrupt_endpoint(client):
    r = client.post("/interrupt")
    assert r.status_code == 200
    assert r.json()["status"] == "interrupted"


def test_health_is_fast(client):
    import time
    start = time.time()
    client.get("/health")
    elapsed = time.time() - start
    assert elapsed < 1.0  # Health check should be fast
