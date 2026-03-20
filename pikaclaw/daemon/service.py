"""Daemon service for background PikaClaw operation."""
from __future__ import annotations


class DaemonService:
    """Background service for scheduled tasks and channel integration."""

    def __init__(self):
        self._running = False

    async def start(self):
        """Start the daemon."""
        self._running = True

    async def stop(self):
        """Stop the daemon."""
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running
