"""SuperAGI integration adapter.

Integrates with a running SuperAGI instance via HTTP API.
Repo: https://github.com/TransformerOptimus/SuperAGI
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass
class SuperAGIResult:
    ok: bool
    data: dict[str, Any]
    error: str = ""
    simulated: bool = False


class SuperAGIClient:
    """HTTP adapter for orchestration/tool-execution via SuperAGI."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        self.base_url = base_url or os.getenv("SUPERAGI_BASE_URL", "http://localhost:8001")
        self.api_key = api_key or os.getenv("SUPERAGI_API_KEY", "")

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def health(self) -> SuperAGIResult:
        """Check if SuperAGI service is reachable."""
        try:
            import requests

            response = requests.get(f"{self.base_url}/health", headers=self._headers(), timeout=8)
            response.raise_for_status()
            return SuperAGIResult(ok=True, data=response.json())
        except Exception as exc:
            return SuperAGIResult(ok=False, data={}, error=str(exc), simulated=True)

    def dispatch_workflow(self, goal: str, context: dict[str, Any] | None = None) -> SuperAGIResult:
        """Send a goal/workflow request to SuperAGI."""
        payload = {"goal": goal, "context": context or {}}
        try:
            import requests

            response = requests.post(
                f"{self.base_url}/workflows/dispatch",
                headers=self._headers(),
                json=payload,
                timeout=20,
            )
            response.raise_for_status()
            return SuperAGIResult(ok=True, data=response.json())
        except Exception as exc:
            return SuperAGIResult(
                ok=False,
                data={"fallback": "local-superagi-simulation", "goal": goal, "context": context or {}},
                error=str(exc),
                simulated=True,
            )
