"""Verifiering av utförda steg."""

from __future__ import annotations

from dataclasses import dataclass

from arviva_agent.executor.executor import StepExecution
from arviva_agent.planner.planner import PlanStep


@dataclass
class VerificationResult:
    ok: bool
    message: str


class Verifier:
    def verify_step(self, step: PlanStep, execution: StepExecution) -> VerificationResult:
        if not execution.ok:
            return VerificationResult(ok=False, message=f"Steg {step.id} misslyckades: {execution.error}")
        if not execution.output.strip():
            return VerificationResult(ok=False, message=f"Steg {step.id} gav tom output")
        return VerificationResult(ok=True, message=f"Steg {step.id} verifierat")
