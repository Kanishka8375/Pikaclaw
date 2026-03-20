"""Desktop API bridge — Python methods exposed to JavaScript."""
from __future__ import annotations
import asyncio
import json
import threading


class PikaClawDesktopAPI:
    """API exposed to frontend via window.pywebview.api."""

    def __init__(self):
        self._window = None
        self._loop = None
        self._agent_loop = None
        self._state = None
        self._interrupted = False

    def set_window(self, window):
        self._window = window

    def _ensure_loop(self):
        if self._agent_loop is None:
            from pikaclaw.config.loader import load_config
            from pikaclaw.core.agent_loop import AgentLoop, LoopState
            from pikaclaw.models.router import ModelRouter
            from pikaclaw.tools.registry import ToolRegistry
            from pikaclaw.agents.registry import AGENTS
            from pikaclaw.security.permissions import PermissionEvaluator

            config = load_config()
            self._agent_loop = AgentLoop(
                model_router=ModelRouter(config),
                tool_registry=ToolRegistry(),
                permission_system=PermissionEvaluator(config),
                agent_registry=AGENTS,
                config=config,
            )
            self._state = LoopState()

    def _emit(self, event_type: str, data: dict):
        if self._window:
            self._window.evaluate_js(
                f"window.dispatchEvent(new CustomEvent('pikaclaw', {{detail: {json.dumps({'type': event_type, **data})}}}));"
            )

    def send_message(self, message: str) -> dict:
        """Send a message to the agent. Returns immediately, streams via events."""
        self._ensure_loop()
        self._interrupted = False

        def _run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._process(message))
            finally:
                loop.close()

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        return {"status": "started"}

    async def _process(self, message: str):
        async for msg in self._agent_loop.run(message, self._state):
            if self._interrupted:
                break
            self._emit(msg.type, {"text": getattr(msg, "text", ""),
                                   "tool": getattr(msg, "tool", ""),
                                   "result": getattr(msg, "result", ""),
                                   "error": getattr(msg, "error", ""),
                                   "turns": getattr(msg, "turns", 0),
                                   "tokens": getattr(msg, "tokens", 0)})

    def switch_agent(self, name: str) -> dict:
        self._ensure_loop()
        from pikaclaw.agents.registry import AGENTS
        if name in AGENTS:
            self._state.active_agent = name
            return {"status": "ok", "agent": name}
        return {"status": "error", "message": f"Unknown agent: {name}"}

    def get_status(self) -> dict:
        self._ensure_loop()
        return {
            "agent": self._state.active_agent,
            "model": self._state.current_model or "",
            "turns": self._state.turn_count,
            "tokens": self._state.total_input_tokens + self._state.total_output_tokens,
            "cost": self._state.total_cost,
            "session_id": self._state.session_id,
        }

    def get_agents(self) -> list[dict]:
        from pikaclaw.agents.registry import AGENTS
        return [{"name": a.name, "display_name": a.display_name, "icon": a.icon,
                 "description": a.description, "mode": a.mode}
                for a in AGENTS.values()]

    def interrupt(self) -> dict:
        self._interrupted = True
        if self._state:
            self._state.interrupted = True
        return {"status": "interrupted"}

    def undo(self) -> dict:
        return {"status": "not_implemented"}

    def redo(self) -> dict:
        return {"status": "not_implemented"}
