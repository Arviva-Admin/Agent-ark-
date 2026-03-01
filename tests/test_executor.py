from arviva_agent.executor.executor import Executor
from arviva_agent.integrations.superagi_client import SuperAGIResult
from arviva_agent.prompts.schemas import PlanStep, VerifySpec
from arviva_agent.planner.planner import PlanStep


class _FakeSuperAGI:
    def dispatch_workflow(self, goal: str, context: dict | None = None) -> SuperAGIResult:
        return SuperAGIResult(ok=True, data={"goal": goal, "status": "queued"})


def test_executor_shell_step() -> None:
    step = PlanStep(
        id=1,
        type="shell",
        description="run pwd",
        command="pwd",
        verify=VerifySpec(type="exit_code", target="command", expect="0"),
    )
    step = PlanStep(id=1, type="shell", action="pwd", tool="shell")
    result = Executor().execute_step(step)
    assert result.ok is True


def test_executor_superagi_step() -> None:
    step = PlanStep(
        id=2,
        type="superagi",
        description="dispatch",
        command="dispatch_workflow",
        verify=VerifySpec(type="stdout_contains", target="stdout", expect="queued"),
    )
    step = PlanStep(id=2, type="orchestrate", action="dispatch", tool="superagi")
    result = Executor(superagi=_FakeSuperAGI()).execute_step(step, goal="Deploy app")
    assert result.ok is True
    assert "Deploy app" in result.output
