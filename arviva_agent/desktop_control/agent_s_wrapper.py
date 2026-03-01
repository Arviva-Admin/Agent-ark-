"""High-level desktop wrapper built on top of Agent-S adapter."""

from __future__ import annotations

from dataclasses import dataclass

from arviva_agent.integrations.agent_s_client import AgentSClient


@dataclass
class DesktopActionResult:
    ok: bool
    details: str


class AgentSWrapper:
    """Facade for GUI actions required by the executor."""

    def __init__(self, client: AgentSClient | None = None) -> None:
        self.client = client or AgentSClient()

    def status(self) -> dict[str, bool]:
        return {"available": self.client.is_available()}

    def click(self, selector: str) -> DesktopActionResult:
        result = self.client.perform_action("click", selector)
        suffix = " [simulated]" if result.simulated else ""
        return DesktopActionResult(ok=result.ok, details=f"{result.message}{suffix}")

    def type_text(self, text: str) -> DesktopActionResult:
        result = self.client.perform_action("type", text)
        suffix = " [simulated]" if result.simulated else ""
        return DesktopActionResult(ok=result.ok, details=f"{result.message}{suffix}")

    def take_screenshot(self) -> DesktopActionResult:
        result = self.client.perform_action("screenshot", "")
        suffix = " [simulated]" if result.simulated else ""
        detail = result.message if not result.screenshot_path else f"{result.message} ({result.screenshot_path})"
        return DesktopActionResult(ok=result.ok, details=f"{detail}{suffix}")
