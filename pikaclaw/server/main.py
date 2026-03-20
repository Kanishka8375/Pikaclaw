"""FastAPI HTTP server for PikaClaw."""
from __future__ import annotations
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="PikaClaw", version="0.1.0")

# Lazy initialization
_loop = None
_state = None


def _get_loop():
    global _loop, _state
    if _loop is None:
        from pikaclaw.config.loader import load_config
        from pikaclaw.core.agent_loop import AgentLoop, LoopState
        from pikaclaw.models.router import ModelRouter
        from pikaclaw.tools.registry import ToolRegistry
        from pikaclaw.agents.registry import AGENTS
        from pikaclaw.security.permissions import PermissionEvaluator

        config = load_config()
        _loop = AgentLoop(
            model_router=ModelRouter(config),
            tool_registry=ToolRegistry(),
            permission_system=PermissionEvaluator(config),
            agent_registry=AGENTS,
            config=config,
        )
        _state = LoopState()
    return _loop, _state


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/status")
async def status():
    _, state = _get_loop()
    return {
        "agent": state.active_agent,
        "model": state.current_model,
        "turns": state.turn_count,
        "tokens": state.total_input_tokens + state.total_output_tokens,
        "cost": state.total_cost,
        "session_id": state.session_id,
    }


@app.get("/agents")
async def list_agents():
    from pikaclaw.agents.registry import AGENTS
    return [{"name": a.name, "display_name": a.display_name, "icon": a.icon,
             "description": a.description, "mode": a.mode}
            for a in AGENTS.values()]


@app.get("/models")
async def list_models():
    from pikaclaw.models.router import MODEL_PROFILES
    return list(MODEL_PROFILES.keys())


class ChatRequest(BaseModel):
    message: str
    agent: str | None = None


@app.post("/chat")
async def chat(req: ChatRequest):
    loop, state = _get_loop()
    if req.agent:
        state.active_agent = req.agent

    async def event_stream():
        async for msg in loop.run(req.message, state):
            data = {"type": msg.type}
            for attr in ("text", "tool", "result", "error", "turns", "tokens", "cost"):
                if hasattr(msg, attr):
                    data[attr] = getattr(msg, attr)
            yield f"data: {json.dumps(data)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


class SwitchRequest(BaseModel):
    name: str


@app.post("/agents/switch")
async def switch_agent(req: SwitchRequest):
    from pikaclaw.agents.registry import AGENTS
    _, state = _get_loop()
    if req.name in AGENTS:
        state.active_agent = req.name
        return {"status": "ok", "agent": req.name}
    return {"status": "error", "message": f"Unknown agent: {req.name}"}


@app.post("/interrupt")
async def interrupt():
    _, state = _get_loop()
    state.interrupted = True
    return {"status": "interrupted"}
