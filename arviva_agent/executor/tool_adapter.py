"""Säkra verktygsadaptrar med allowlist/denylist."""

from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ToolResult:
    ok: bool
    output: str
    error: str = ""
    return_code: int = 0


class SecureToolAdapter:
    """Kör shell/python med säkerhetspolicy för kommandon."""

    def __init__(self, allowlist: set[str] | None = None, denylist: set[str] | None = None, timeout_s: int = 30) -> None:
        self.allowlist = allowlist or {"echo", "pwd", "ls", "python", "python3", "cat", "test"}
        self.denylist = denylist or {"rm", "shutdown", "reboot", "mkfs", "dd"}
        self.blocked_fragments = ["rm -rf", "mkfs", "shutdown", "reboot", "dd if=", "chmod 777 /", ":(){:|:&};:"]
        self.timeout_s = timeout_s

    def _validate(self, command: str) -> tuple[bool, str]:
        lower = command.lower()
        for fragment in self.blocked_fragments:
            if fragment in lower:
                return False, f"Kommando blockerat av policy: {fragment}"

        args = shlex.split(command)
        if not args:
            return False, "Tomt kommando"

        binary = Path(args[0]).name
        if binary in self.denylist:
            return False, f"Kommando blockerat: {binary}"
        if binary not in self.allowlist:
            return False, f"Kommando ej tillåtet: {binary}"
        return True, ""

    def run_shell(self, command: str) -> ToolResult:
        valid, message = self._validate(command)
        if not valid:
            return ToolResult(ok=False, output="", error=message, return_code=126)

        try:
            completed = subprocess.run(
                shlex.split(command),
                capture_output=True,
                text=True,
                timeout=self.timeout_s,
                check=False,
            )
            return ToolResult(
                ok=completed.returncode == 0,
                output=completed.stdout,
                error=completed.stderr,
                return_code=completed.returncode,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(ok=False, output="", error="Timeout vid shell-körning", return_code=124)

    def run_python(self, code: str) -> ToolResult:
        """Kör begränsad Python-kod i separat process."""
        result = self.run_shell(f"python3 -c {shlex.quote(code)}")
        return result
