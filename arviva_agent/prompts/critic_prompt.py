"""Critic prompt and deterministic policy checks."""

from __future__ import annotations

from arviva_agent.prompts.schemas import CriticResult, Plan
from arviva_agent.prompts.system_policy import SYSTEM_POLICY

BLOCKED_PATTERNS = ["rm -rf", "shutdown", "reboot", "mkfs", "dd if=", "chmod 777 /"]


def build_critic_prompt(plan_json: str, integrations_status: dict[str, object]) -> str:
    return (
        f"{SYSTEM_POLICY}\n"
        "ROLE: CRITIC\n"
        "Validate plan safety/risk and return JSON schema: {ok, risk_level, issues, patched_plan}.\n"
        f"PLAN_JSON: {plan_json}\n"
        f"INTEGRATIONS_STATUS: {integrations_status}\n"
    )


def deterministic_critic(plan: Plan) -> CriticResult:
    issues: list[str] = []
    patched = plan.copy(deep=True)
    risk_level = "low"

    for step in patched.steps:
        lower_command = step.command.lower()
        for pattern in BLOCKED_PATTERNS:
            if pattern in lower_command:
                issues.append(f"Step {step.id} innehåller blockerat mönster: {pattern}")
                risk_level = "high"
                step.type = "python"
                step.command = "print('Blocked destructive command replaced by critic')"
                step.description = "Destruktivt kommando ersatt av säker fallback"
                step.simulated = True

    ok = len(issues) == 0
    return CriticResult(ok=ok, risk_level=risk_level, issues=issues, patched_plan=None if ok else patched)
