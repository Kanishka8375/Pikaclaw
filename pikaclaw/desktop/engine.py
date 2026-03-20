"""JSON-RPC engine for stdin/stdout communication (Tauri-ready)."""
from __future__ import annotations
import json
import sys


class DesktopEngine:
    """Reads JSON-RPC from stdin, writes responses to stdout."""

    def __init__(self):
        self.api = None

    def start(self):
        from pikaclaw.desktop.api import PikaClawDesktopAPI
        self.api = PikaClawDesktopAPI()

        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                method = request.get("method", "")
                params = request.get("params", {})
                req_id = request.get("id", None)

                handler = getattr(self.api, method, None)
                if handler:
                    result = handler(**params) if isinstance(params, dict) else handler(*params)
                    self._respond(req_id, result)
                else:
                    self._error(req_id, f"Unknown method: {method}")
            except Exception as e:
                self._error(None, str(e))

    def _respond(self, req_id, result):
        print(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}), flush=True)

    def _error(self, req_id, message):
        print(json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"message": message}}), flush=True)
