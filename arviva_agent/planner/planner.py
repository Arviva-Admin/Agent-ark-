"""Planner med prompt-stack, strict JSON och tool gating."""

from __future__ import annotations

import json

from arviva_agent.planner.llm_interface import LLMClient, build_llm_client
from arviva_agent.prompts.critic_prompt import deterministic_critic
from arviva_agent.prompts.planner_prompt import build_planner_prompt, build_repair_prompt
from arviva_agent.prompts.schemas import AgentSAction, CriticResult, Plan, PlanStep


class Planner:
    """LLM-baserad planeringsmotor med strikt schema-validering."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or build_llm_client()

    def _parse_plan_json(self, raw: str) -> Plan:
        data = json.loads(raw)
        plan = Plan(**data)
        self._enforce_tool_gating(plan)
        return plan

    def _enforce_tool_gating(self, plan: Plan) -> None:
        for step in plan.steps:
            # exakt ett tool per steg via `type` + agent_s_action endast för agent_s.
            if step.type == "agent_s" and step.agent_s_action is None:
                step.agent_s_action = AgentSAction(action="screenshot", target="", text="")
            if step.type != "agent_s":
                step.agent_s_action = None

    def create_plan_llm(self, goal: str, context_summary: str, integrations_status: dict[str, object]) -> Plan:
        if not goal.strip():
            raise ValueError("Goal får inte vara tomt")

        prompt = build_planner_prompt(goal, context_summary, integrations_status)
        raw = self.llm_client.generate(prompt)

        try:
            return self._parse_plan_json(raw)
        except Exception:
            repaired_raw = self.llm_client.generate(build_repair_prompt(raw))
            try:
                return self._parse_plan_json(repaired_raw)
            except Exception as exc:
                raise ValueError("Planner kunde inte skapa giltig JSON-plan") from exc

    def review_plan_with_critic(self, plan: Plan) -> CriticResult:
        return deterministic_critic(plan)

    def generate(self, goal: str, context_summary: str = "", integrations_status: dict[str, object] | None = None) -> Plan:
        return self.create_plan_llm(goal, context_summary, integrations_status or {})


__all__ = ["Planner", "Plan", "PlanStep", "CriticResult"]
