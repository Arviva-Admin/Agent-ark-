"""Agent-S integration adapter.

This module provides a thin, testable contract around the real Agent-S repository
(https://github.com/simular-ai/Agent-S). It supports:
1) Local repo + CLI bridge mode
2) Simulated fallback mode (explicitly marked)
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AgentSActionResult:
    ok: bool
    message: str
    screenshot_path: str | None = None
    simulated: bool = False


class AgentSClient:
    """Adapter for desktop actions powered by Agent-S."""

    def __init__(self, repo_path: str | None = None) -> None:
        self.repo_path = Path(repo_path or os.getenv("AGENT_S_REPO_PATH", "third_party/Agent-S"))

    def is_available(self) -> bool:
        """Detect whether local Agent-S repo is available."""
        return self.repo_path.exists()

    def perform_action(self, action: str, payload: str = "") -> AgentSActionResult:
        """Execute desktop action through Agent-S CLI bridge."""
        if not self.is_available():
            return AgentSActionResult(
                ok=True,
                message=f"Agent-S saknas på {self.repo_path}; kör simulerat läge",
                simulated=True,
            )

        command = [
            "python3",
            "scripts/run_action.py",
            "--action",
            action,
            "--payload",
            payload,
        ]
        try:
            completed = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=45,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return AgentSActionResult(ok=False, message="Agent-S action timeout")

        if completed.returncode != 0:
            return AgentSActionResult(ok=False, message=completed.stderr.strip() or "Agent-S action failed")

        out = completed.stdout.strip()
        try:
            data = json.loads(out)
            return AgentSActionResult(
                ok=bool(data.get("ok", True)),
                message=str(data.get("message", "ok")),
                screenshot_path=data.get("screenshot_path"),
                simulated=bool(data.get("simulated", False)),
            )
        except json.JSONDecodeError:
            return AgentSActionResult(ok=True, message=out or "Agent-S action completed")
