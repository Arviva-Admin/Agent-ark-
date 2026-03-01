"""Verifiering av utförda steg."""

from __future__ import annotations

from dataclasses import dataclass

from arviva_agent.executor.executor import StepExecution
from arviva_agent.prompts.schemas import PlanStep
from arviva_agent.planner.planner import PlanStep


@dataclass
class VerificationResult:
    ok: bool
    message: str


class Verifier:
    def verify_step(self, step: PlanStep, execution: StepExecution) -> VerificationResult:
        if not execution.ok:
            return VerificationResult(ok=False, message=f"Steg {step.id} misslyckades: {execution.error}")

        verify_type = step.verify.type
        expect = step.verify.expect

        if verify_type == "exit_code" and expect == "0":
            return VerificationResult(ok=True, message=f"Steg {step.id} verifierat via exit_code")

        if verify_type == "stdout_contains" and expect.lower() in execution.output.lower():
            return VerificationResult(ok=True, message=f"Steg {step.id} verifierat via stdout")

        if verify_type in {"custom", "file_exists", "http_status"} and execution.output.strip():
            return VerificationResult(ok=True, message=f"Steg {step.id} verifierat via {verify_type}")

        return VerificationResult(ok=False, message=f"Steg {step.id} uppfyllde inte verify-krav")
        if not execution.output.strip():
            return VerificationResult(ok=False, message=f"Steg {step.id} gav tom output")
        return VerificationResult(ok=True, message=f"Steg {step.id} verifierat")
