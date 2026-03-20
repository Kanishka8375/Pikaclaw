"""The master agent loop — heart of PikaClaw."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import AsyncIterator
from uuid import uuid4

from pikaclaw.core.messages import (
    TextMessage, ToolCallMessage, ToolResultMessage,
    DoneMessage, ErrorMessage, FeedbackMessage,
)
from pikaclaw.core.system_prompt import SystemPromptBuilder

# Type checking imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pikaclaw.models.router import ModelRouter
    from pikaclaw.tools.registry import ToolRegistry
    from pikaclaw.security.permissions import PermissionEvaluator
    from pikaclaw.context.manager import ContextManager
    from pikaclaw.memory.sessions import SessionManager
    from pikaclaw.agents.base import AgentDefinition
    from pikaclaw.config.schema import PikaClawConfig


@dataclass
class LoopState:
    """Mutable state for an agent loop session."""
    messages: list = field(default_factory=list)
    turn_count: int = 0
    max_turns: int = 250
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost: float = 0.0
    active_agent: str = "build"
    session_id: str = field(default_factory=lambda: str(uuid4())[:8])
    interrupted: bool = False
    current_model: str | None = None
    context_usage_percent: float = 0.0


class AgentLoop:
    """Single-threaded agent loop. Pattern: send->receive->tool->repeat."""

    def __init__(
        self,
        model_router: ModelRouter,
        tool_registry: ToolRegistry,
        permission_system: PermissionEvaluator | None = None,
        context_manager: ContextManager | None = None,
        memory: SessionManager | None = None,
        agent_registry: dict[str, AgentDefinition] | None = None,
        config: PikaClawConfig | None = None,
    ):
        self.router = model_router
        self.tools = tool_registry
        self.permissions = permission_system
        self.context = context_manager
        self.memory = memory
        self.agents = agent_registry or {}
        self.config = config
        self.prompt_builder = SystemPromptBuilder()

        # Lazy imports for security components
        self._sanitizer = None
        self._sentinel = None
        self._audit = None
        self._signal_detector = None
        self._feedback_collector = None

    @property
    def sanitizer(self):
        if self._sanitizer is None:
            try:
                from pikaclaw.security.secrets import SecretSanitizer
                self._sanitizer = SecretSanitizer()
            except ImportError:
                self._sanitizer = None
        return self._sanitizer

    @property
    def sentinel(self):
        if self._sentinel is None:
            try:
                from pikaclaw.security.sentinel import Sentinel
                self._sentinel = Sentinel()
            except ImportError:
                self._sentinel = None
        return self._sentinel

    @property
    def audit(self):
        if self._audit is None:
            try:
                from pikaclaw.security.audit import AuditLogger
                self._audit = AuditLogger()
            except ImportError:
                self._audit = None
        return self._audit

    @property
    def signal_detector(self):
        if self._signal_detector is None:
            try:
                from pikaclaw.feedback.signals import ImplicitSignalDetector
                self._signal_detector = ImplicitSignalDetector()
            except ImportError:
                self._signal_detector = None
        return self._signal_detector

    @property
    def feedback_collector(self):
        if self._feedback_collector is None:
            try:
                from pikaclaw.feedback.collector import FeedbackCollector
                self._feedback_collector = FeedbackCollector()
            except ImportError:
                self._feedback_collector = None
        return self._feedback_collector

    def _get_agent(self, state: LoopState) -> AgentDefinition:
        """Get the active agent definition."""
        agent = self.agents.get(state.active_agent)
        if not agent:
            # Fall back to build agent or create a minimal one
            agent = self.agents.get("build")
        if not agent:
            from pikaclaw.agents.base import AgentDefinition
            agent = AgentDefinition(
                name="build", display_name="Build", description="Default agent",
                icon="⚡", mode="primary", system_prompt="You are a coding assistant.",
            )
        return agent

    def _build_tool_definitions(self, agent) -> list[dict]:
        """Build tool definitions respecting agent permissions."""
        all_tools = self.tools.list_tools()
        # Filter out denied tools
        if agent.denied_tools:
            all_tools = [t for t in all_tools if t["name"] not in agent.denied_tools]
        # Filter by write permission
        if not agent.can_write_files:
            all_tools = [t for t in all_tools if t["name"] not in ("Write", "Edit")]
        if not agent.can_execute_bash:
            all_tools = [t for t in all_tools if t["name"] != "Bash"]
        return all_tools

    async def run(self, prompt: str, state: LoopState) -> AsyncIterator:
        """Run the agent loop. Yields Message objects."""
        try:
            agent = self._get_agent(state)

            # Build system prompt
            system_prompt = self.prompt_builder.build(agent, state, self.config)

            # Build tool definitions for this agent
            tool_defs = self._build_tool_definitions(agent)

            # Determine model
            model = agent.preferred_model or (self.config.default_model if self.config else None)
            state.current_model = model

            # Add user message to conversation
            state.messages.append({"role": "user", "content": prompt})

            # Detect implicit frustration signals in user message
            if self.signal_detector:
                last_error = None
                if len(state.messages) >= 2:
                    prev = state.messages[-2]
                    if prev.get("role") == "tool" and "error" in str(prev.get("content", "")).lower():
                        last_error = prev.get("content", "")[:200]

                signals = self.signal_detector.analyze_message(prompt, context={
                    "agent": state.active_agent,
                    "turn_count": state.turn_count,
                    "last_tool_error": last_error,
                })
                for signal in signals:
                    # Record as implicit feedback
                    if self.feedback_collector:
                        # Build conversation snippet for context
                        snippet = "\n".join(
                            f"{m.get('role', '?')}: {str(m.get('content', ''))[:100]}"
                            for m in state.messages[-4:]
                        )
                        try:
                            await self.feedback_collector.submit(
                                rating=0,
                                category=signal.category,
                                comment=signal.description,
                                session_id=state.session_id,
                                agent=state.active_agent,
                                model=state.current_model or "",
                                turn_count=state.turn_count,
                                conversation_snippet=snippet,
                                source="implicit",
                            )
                        except Exception:
                            pass

                    yield FeedbackMessage(
                        signal_type=signal.signal_type,
                        category=signal.category,
                        confidence=signal.confidence,
                        description=signal.description,
                    )

            # Agent loop: keep going until model responds with text only (no tool calls)
            while state.turn_count < state.max_turns and not state.interrupted:
                state.turn_count += 1

                # Format tools for the API call
                formatted_tools = None
                if tool_defs:
                    # Determine format based on provider
                    provider_name = "ollama"
                    if model and "/" in model:
                        provider_name = model.split("/")[0]
                    elif model and model.startswith("claude"):
                        provider_name = "anthropic"

                    if provider_name == "anthropic":
                        formatted_tools = [
                            {"name": t["name"], "description": t["description"], "input_schema": t["parameters"]}
                            for t in tool_defs
                        ]
                    else:
                        formatted_tools = [
                            {"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["parameters"]}}
                            for t in tool_defs
                        ]

                # Call the model
                try:
                    response = await self.router.complete(
                        messages=state.messages,
                        model=model,
                        tools=formatted_tools,
                        system=system_prompt,
                    )
                except Exception as e:
                    yield ErrorMessage(error=f"Model call failed: {e}")
                    break

                # Track usage
                usage = response.get("usage", {})
                state.total_input_tokens += usage.get("input_tokens", 0)
                state.total_output_tokens += usage.get("output_tokens", 0)

                content = response.get("content", "")
                tool_calls = response.get("tool_calls", [])

                # Yield text response
                if content and content.strip():
                    # Sanitize secrets from response
                    if self.sanitizer:
                        content = self.sanitizer.sanitize(content)
                    yield TextMessage(text=content, model=model or "")

                # If no tool calls, we're done
                if not tool_calls:
                    # Add assistant message to history
                    state.messages.append({"role": "assistant", "content": content or ""})
                    break

                # Process tool calls
                # Build assistant message with tool calls for history
                assistant_msg = {"role": "assistant", "content": content or ""}
                # For Ollama/OpenAI format, add tool_calls to message
                # For simplicity, we store them separately
                state.messages.append(assistant_msg)

                for tc in tool_calls:
                    tool_name = tc.get("name", tc.get("function", {}).get("name", ""))
                    tool_input = tc.get("input", tc.get("arguments", tc.get("function", {}).get("arguments", {})))
                    call_id = tc.get("id", str(uuid4())[:8])

                    # Parse arguments if string
                    if isinstance(tool_input, str):
                        try:
                            tool_input = json.loads(tool_input)
                        except (json.JSONDecodeError, TypeError):
                            tool_input = {"raw": tool_input}

                    yield ToolCallMessage(tool=tool_name, input=tool_input, call_id=call_id)

                    # Check permissions
                    result_text = ""
                    is_error = False

                    if self.permissions:
                        perm = self.permissions.evaluate(tool_name, tool_input, agent)
                        if perm == "deny":
                            result_text = f"Permission denied: {tool_name} is not allowed for the {agent.name} agent."
                            is_error = True

                    # Check sentinel for file operations
                    if not is_error and self.sentinel and tool_name in ("Write", "Edit"):
                        file_path = tool_input.get("file_path", "")
                        if self.sentinel.is_protected_path(file_path):
                            result_text = f"Protected file: {file_path} cannot be modified."
                            is_error = True

                    # Execute tool
                    if not is_error:
                        tool = self.tools.get(tool_name)
                        if tool:
                            try:
                                result_text = await tool.execute(tool_input)
                            except Exception as e:
                                result_text = f"Tool error: {e}"
                                is_error = True
                        else:
                            result_text = f"Unknown tool: {tool_name}"
                            is_error = True

                    # Sanitize secrets from tool output
                    if self.sanitizer and result_text:
                        result_text = self.sanitizer.sanitize(result_text)

                    # Log to audit
                    if self.audit:
                        try:
                            self.audit.log_event(
                                action=f"tool_{tool_name}",
                                resource=str(tool_input)[:200],
                                result="error" if is_error else "ok",
                            )
                        except Exception:
                            pass

                    yield ToolResultMessage(
                        tool=tool_name, result=result_text,
                        is_error=is_error, call_id=call_id,
                    )

                    # Add tool result to conversation for next model call
                    state.messages.append({
                        "role": "tool",
                        "content": result_text,
                        "tool_call_id": call_id,
                        "name": tool_name,
                    })

            # Done
            yield DoneMessage(
                turns=state.turn_count,
                tokens=state.total_input_tokens + state.total_output_tokens,
                cost=state.total_cost,
            )

        except Exception as e:
            yield ErrorMessage(error=str(e))
