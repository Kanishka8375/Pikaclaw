"""MCP Security Gateway — stub for MCP tool sandboxing."""
from __future__ import annotations


class MCPSecurityGateway:
    """Security gateway for MCP tool calls."""

    def __init__(self):
        self.trusted_servers: dict[str, dict] = {}

    def register_server(self, name: str, config: dict):
        self.trusted_servers[name] = config

    def is_trusted(self, server: str) -> bool:
        return server in self.trusted_servers

    def validate_input(self, server: str, tool: str, input_data: dict) -> tuple[bool, str]:
        if not self.is_trusted(server):
            return False, f"Server '{server}' is not trusted"
        return True, ""

    def sanitize_output(self, output: str) -> str:
        from pikaclaw.security.secrets import SecretSanitizer
        return SecretSanitizer().sanitize(output)
