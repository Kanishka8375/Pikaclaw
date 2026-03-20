"""Agent spawn tool."""
from __future__ import annotations


class AgentSpawnTool:
    """Spawn a sub-agent to handle a task."""

    name = "AgentSpawn"
    description = "Spawn a sub-agent to handle a specific task."
    parameters = {
        "type": "object",
        "properties": {
            "agent": {"type": "string", "description": "Name or type of agent to spawn."},
            "prompt": {"type": "string", "description": "The prompt/task for the spawned agent."},
        },
        "required": ["agent", "prompt"],
    }

    async def execute(self, params: dict) -> str:
        try:
            agent = params["agent"]
            prompt = params["prompt"]
            return f"__AGENT_SPAWN__: Spawning agent '{agent}' with prompt: {prompt}"
        except Exception as e:
            return f"Error in agent_spawn: {e}"
