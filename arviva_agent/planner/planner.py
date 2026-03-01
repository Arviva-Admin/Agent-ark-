"""Planner: genererar JSON-planer från naturligt språk."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from arviva_agent.planner.llm_interface import LLMClient, build_llm_client


@dataclass
class PlanStep:
    id: int
    type: str
    action: str
    tool: str


@dataclass
class Plan:
    goal: str
    steps: list[PlanStep]


class Planner:
    """LLM-baserad planeringsmotor med strikt JSON-validering."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or build_llm_client()

    def generate(self, goal: str) -> Plan:
        if not goal.strip():
            raise ValueError("Goal får inte vara tomt")

        prompt = (
            "Returnera ENDAST JSON med schema {goal, steps:[{id,type,action,tool}]}.\n"
            f"GOAL: {goal}"
        )
        raw = self.llm_client.generate(prompt)

        parsed: dict[str, Any] = json.loads(raw)
        steps_raw = parsed.get("steps", [])
        if not steps_raw:
            raise ValueError("Planner genererade ingen plan")

        steps = [
            PlanStep(
                id=int(step["id"]),
                type=str(step["type"]),
                action=str(step["action"]),
                tool=str(step["tool"]),
            )
            for step in steps_raw
        ]
        return Plan(goal=str(parsed.get("goal", goal)), steps=steps)
