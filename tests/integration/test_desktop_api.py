"""Tests for the desktop API bridge."""
import pytest
from pikaclaw.desktop.api import PikaClawDesktopAPI


@pytest.fixture
def api():
    return PikaClawDesktopAPI()


def test_api_creation(api):
    assert api._window is None
    assert api._agent_loop is None


def test_get_agents(api):
    agents = api.get_agents()
    assert isinstance(agents, list)
    assert len(agents) == 9
    names = [a["name"] for a in agents]
    assert "build" in names


def test_switch_agent_valid(api):
    result = api.switch_agent("plan")
    assert result["status"] == "ok"
    assert result["agent"] == "plan"


def test_switch_agent_invalid(api):
    result = api.switch_agent("nonexistent")
    assert result["status"] == "error"


def test_get_status(api):
    status = api.get_status()
    assert "agent" in status
    assert "turns" in status
    assert "tokens" in status
    assert "session_id" in status


def test_interrupt(api):
    result = api.interrupt()
    assert result["status"] == "interrupted"


def test_undo_not_implemented(api):
    result = api.undo()
    assert result["status"] == "not_implemented"


def test_redo_not_implemented(api):
    result = api.redo()
    assert result["status"] == "not_implemented"
