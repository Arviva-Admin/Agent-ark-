from arviva_agent.orchestrator.orchestrator import Orchestrator


def test_orchestrator_runs_goal() -> None:
    status = {
        "agent_s": {"reachable": False, "mode": "simulated"},
        "superagi": {"reachable": False, "mode": "simulated", "url": "http://localhost:8001"},
    }
    result = Orchestrator().run("Verifiera arbetsmiljö", max_iterations=20, integrations_status=status)
    assert result.status in {"completed", "incomplete"}
    result = Orchestrator().run("Verifiera arbetsmiljö", max_iterations=20)
    assert result.status in {"completed", "needs_replan"}
    assert result.completed_steps >= 0
