from arviva_agent.orchestrator.orchestrator import Orchestrator


def test_orchestrator_runs_goal() -> None:
    result = Orchestrator().run("Verifiera arbetsmiljö", max_iterations=20)
    assert result.status in {"completed", "needs_replan"}
    assert result.completed_steps >= 0
