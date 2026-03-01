from arviva_agent.planner.planner import Planner


def test_planner_generates_valid_json_plan_schema() -> None:
    plan = Planner().create_plan_llm(
        goal="Automatisera release",
        context_summary="",
        integrations_status={"agent_s": {"reachable": False}, "superagi": {"reachable": False}},
    )
    assert plan.goal
    assert len(plan.steps) >= 1
    for step in plan.steps:
        assert step.type in {"shell", "python", "agent_s", "superagi"}
        assert step.verify is not None
def test_planner_generates_valid_plan() -> None:
    plan = Planner().generate("Automatisera release")
    assert plan.goal
    assert len(plan.steps) >= 4
    tools = {step.tool for step in plan.steps}
    assert "agent_s" in tools
    assert "superagi" in tools
