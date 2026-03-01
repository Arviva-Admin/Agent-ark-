"""Schemas for strict planner/critic JSON validation.

Uses pydantic when available; falls back to lightweight local validators.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

ToolType = Literal["shell", "python", "agent_s", "superagi"]
VerifyType = Literal["stdout_contains", "exit_code", "http_status", "file_exists", "custom"]
RiskLevel = Literal["low", "medium", "high"]

_ALLOWED_TOOLS = {"shell", "python", "agent_s", "superagi"}
_ALLOWED_VERIFY = {"stdout_contains", "exit_code", "http_status", "file_exists", "custom"}

try:
    from pydantic import BaseModel, Field

    class VerifySpec(BaseModel):
        type: VerifyType
        target: str
        expect: str

    class AgentSAction(BaseModel):
        action: str = Field(default="screenshot")
        target: str = Field(default="")
        text: str = Field(default="")

    class PlanStep(BaseModel):
        id: int
        type: ToolType
        description: str
        command: str = ""
        agent_s_action: AgentSAction | None = None
        simulated: bool = False
        verify: VerifySpec

    class Plan(BaseModel):
        goal: str
        assumptions: list[str] = Field(default_factory=list)
        steps: list[PlanStep]

    class CriticResult(BaseModel):
        ok: bool
        risk_level: RiskLevel
        issues: list[str] = Field(default_factory=list)
        patched_plan: Plan | None = None

except Exception:

    @dataclass
    class VerifySpec:
        type: str
        target: str
        expect: str

        def __post_init__(self) -> None:
            if self.type not in _ALLOWED_VERIFY:
                raise ValueError(f"Invalid verify type: {self.type}")

    @dataclass
    class AgentSAction:
        action: str = "screenshot"
        target: str = ""
        text: str = ""

    @dataclass
    class PlanStep:
        id: int
        type: str
        description: str
        command: str = ""
        agent_s_action: AgentSAction | None = None
        simulated: bool = False
        verify: VerifySpec = field(default_factory=lambda: VerifySpec("custom", "", ""))

        def __post_init__(self) -> None:
            if self.type not in _ALLOWED_TOOLS:
                raise ValueError(f"Invalid tool type: {self.type}")
            if isinstance(self.agent_s_action, dict):
                self.agent_s_action = AgentSAction(**self.agent_s_action)
            if isinstance(self.verify, dict):
                self.verify = VerifySpec(**self.verify)

        def dict(self) -> dict:
            return asdict(self)

    @dataclass
    class Plan:
        goal: str
        assumptions: list[str] = field(default_factory=list)
        steps: list[PlanStep] = field(default_factory=list)

        def __post_init__(self) -> None:
            parsed: list[PlanStep] = []
            for step in self.steps:
                parsed.append(step if isinstance(step, PlanStep) else PlanStep(**step))
            self.steps = parsed

        def copy(self, deep: bool = True) -> "Plan":
            return Plan(**asdict(self))

    @dataclass
    class CriticResult:
        ok: bool
        risk_level: str
        issues: list[str] = field(default_factory=list)
        patched_plan: Plan | None = None

        def __post_init__(self) -> None:
            if self.risk_level not in {"low", "medium", "high"}:
                raise ValueError("Invalid risk level")
