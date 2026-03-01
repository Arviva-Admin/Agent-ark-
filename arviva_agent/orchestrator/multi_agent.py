"""Minimal multi-agent-koordination inspirerad av SuperAGI-principer."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AgentRole:
    name: str
    responsibility: str


class MultiAgentCoordinator:
    def __init__(self) -> None:
        self.roles = [
            AgentRole(name="planner", responsibility="planering"),
            AgentRole(name="executor", responsibility="verktygskörning"),
            AgentRole(name="verifier", responsibility="kvalitetssäkring"),
        ]

    def describe(self) -> list[dict[str, str]]:
        return [{"name": role.name, "responsibility": role.responsibility} for role in self.roles]
