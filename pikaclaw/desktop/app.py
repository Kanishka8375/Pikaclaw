"""Desktop app launcher using pywebview."""
from __future__ import annotations
from pathlib import Path


def launch():
    """Launch PikaClaw desktop window."""
    try:
        import webview
    except ImportError:
        raise RuntimeError(
            "pywebview not installed. Install with: pip install pywebview\n"
            "Or use terminal mode: pikaclaw chat"
        )

    from pikaclaw.desktop.api import PikaClawDesktopAPI

    api = PikaClawDesktopAPI()
    frontend = Path(__file__).parent / "frontend" / "index.html"

    if not frontend.exists():
        raise FileNotFoundError(f"Frontend not found at {frontend}")

    window = webview.create_window(
        "PikaClaw",
        str(frontend),
        js_api=api,
        width=1200,
        height=800,
        min_size=(800, 600),
    )
    api.set_window(window)
    webview.start(debug=False)
