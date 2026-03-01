from arviva_agent.planner.planner import Planner


def test_planner_generates_valid_plan() -> None:
    plan = Planner().generate("Automatisera release")
    assert plan.goal
    assert len(plan.steps) >= 4
    tools = {step.tool for step in plan.steps}
    assert "agent_s" in tools
    assert "superagi" in tools
