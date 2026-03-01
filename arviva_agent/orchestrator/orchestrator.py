"""Huvudorkestrator för autonom körning med prompt-stack och repair-cykel."""
"""Huvudorkestrator för autonom körning, felhantering och rollback/replan."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from arviva_agent.executor.executor import Executor
from arviva_agent.memory.memory_store import MemoryStore
from arviva_agent.orchestrator.multi_agent import MultiAgentCoordinator
from arviva_agent.planner.planner import Plan, Planner
from arviva_agent.prompts.compressor import compress_events
from arviva_agent.prompts.schemas import PlanStep
from arviva_agent.validator.feedback import FeedbackPolicy
from arviva_agent.validator.verifier import Verifier


@dataclass
class RunResult:
    status: str
    completed_steps: int
    message: str


class Orchestrator:
    def __init__(
        self,
        planner: Planner | None = None,
        executor: Executor | None = None,
        verifier: Verifier | None = None,
        feedback: FeedbackPolicy | None = None,
        memory: MemoryStore | None = None,
    ) -> None:
        self.planner = planner or Planner()
        self.executor = executor or Executor()
        self.verifier = verifier or Verifier()
        self.feedback = feedback or FeedbackPolicy()
        self.memory = memory or MemoryStore()
        self.coordinator = MultiAgentCoordinator()

    def _run_step(self, step: PlanStep, goal: str) -> tuple[bool, str]:
        execution = self.executor.execute_step(step, goal=goal)
        self.memory.append("step_executed", {"step": step.dict(), "execution": asdict(execution)})

        verification = self.verifier.verify_step(step, execution)
        self.memory.append("step_verified", {"step_id": step.id, "verification": asdict(verification)})
        return verification.ok, verification.message

    def run(
        self,
        goal: str,
        max_iterations: int = 20,
        integrations_status: dict[str, Any] | None = None,
    ) -> RunResult:
        integrations_status = integrations_status or {}
        context_summary = ""
        completed = 0
        iterations = 0

        plan: Plan = self.planner.create_plan_llm(
            goal=goal,
            context_summary=context_summary,
            integrations_status=integrations_status,
        )

        critic = self.planner.review_plan_with_critic(plan)
        if not critic.ok and critic.patched_plan is not None:
            self.memory.append("critic_patch_applied", {"issues": critic.issues, "risk_level": critic.risk_level})
            plan = critic.patched_plan

        while iterations < max_iterations:
            for step in plan.steps:
                if iterations >= max_iterations:
                    return RunResult(status="incomplete", completed_steps=completed, message="Nådde iterationsgräns")

                iterations += 1
                ok, message = self._run_step(step, goal=goal)
                context_summary = compress_events(self.memory.recent_events(), limit=8, max_chars=1200)

                if ok:
                    completed += 1
                    self.memory.embed_and_store(
                        key=f"step-{step.id}-{iterations}",
                        text=f"{step.description} {message}",
                        payload={"step_id": step.id, "ok": ok, "summary": context_summary},
                    )
                    continue

                self.memory.append("repair_cycle", {"failed_step": step.id, "observation": message})
                repair_goal = f"{goal}. Failure observation: {message}"
                plan = self.planner.create_plan_llm(
                    goal=repair_goal,
                    context_summary=context_summary,
                    integrations_status=integrations_status,
                )
                critic_repair = self.planner.review_plan_with_critic(plan)
                if not critic_repair.ok and critic_repair.patched_plan is not None:
                    plan = critic_repair.patched_plan
                break
            else:
                return RunResult(status="completed", completed_steps=completed, message="Mål slutfört")

        return RunResult(status="incomplete", completed_steps=completed, message="Nådde iterationsgräns")
    def run(self, goal: str, max_iterations: int = 20) -> RunResult:
        plan: Plan = self.planner.generate(goal)
        self.memory.append("plan_created", {"goal": plan.goal, "steps": [asdict(s) for s in plan.steps]})

        completed = 0
        retries_by_step: dict[int, int] = {}

        for step in plan.steps:
            if completed >= max_iterations:
                return RunResult(status="incomplete", completed_steps=completed, message="Nådde iterationsgräns")

            while True:
                execution = self.executor.execute_step(step, goal=goal)
                self.memory.append("step_executed", {"step": asdict(step), "execution": asdict(execution)})
                verification = self.verifier.verify_step(step, execution)
                retries = retries_by_step.get(step.id, 0)
                decision = self.feedback.decide(verification, retries=retries)
                self.memory.append(
                    "feedback_decision",
                    {"step_id": step.id, "verification": asdict(verification), "decision": asdict(decision)},
                )

                if decision.action == "continue":
                    completed += 1
                    self.memory.embed_and_store(
                        key=f"step-{step.id}",
                        text=f"{step.action} {execution.output}",
                        payload={"step_id": step.id, "output": execution.output},
                    )
                    break

                if decision.action == "retry":
                    retries_by_step[step.id] = retries + 1
                    continue

                # repair/replan-strategi: avbryt säkert och signalera replan.
                if decision.action == "replan":
                    return RunResult(
                        status="needs_replan",
                        completed_steps=completed,
                        message=f"Steg {step.id} kräver replan: {decision.reason}",
                    )

                return RunResult(status="failed", completed_steps=completed, message=decision.reason)

        return RunResult(status="completed", completed_steps=completed, message="Mål slutfört")
