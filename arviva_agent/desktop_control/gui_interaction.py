"""GUI-interaktion ovanpå AgentSWrapper."""

from __future__ import annotations

from dataclasses import dataclass

from arviva_agent.desktop_control.agent_s_wrapper import AgentSWrapper


@dataclass
class GUICommand:
    action: str
    payload: str


class GUIInteraction:
    def __init__(self, agent_s: AgentSWrapper | None = None) -> None:
        self.agent_s = agent_s or AgentSWrapper()

    def execute(self, command: GUICommand) -> tuple[bool, str]:
        if command.action == "click":
            result = self.agent_s.click(command.payload)
            return result.ok, result.details
        if command.action == "type":
            result = self.agent_s.type_text(command.payload)
            return result.ok, result.details
        if command.action == "screenshot":
            result = self.agent_s.take_screenshot()
            return result.ok, result.details
        return False, f"Okänd GUI-action: {command.action}"
