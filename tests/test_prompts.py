from arviva_agent.executor.tool_adapter import SecureToolAdapter
from arviva_agent.planner.planner import Planner
from arviva_agent.prompts.critic_prompt import deterministic_critic
from arviva_agent.prompts.schemas import Plan, PlanStep, VerifySpec


def test_tool_gating_allows_only_known_types() -> None:
    plan = Planner().create_plan_llm("goal", "", {"agent_s": {}, "superagi": {}})
    assert all(step.type in {"shell", "python", "agent_s", "superagi"} for step in plan.steps)


def test_critic_blocks_destructive_commands() -> None:
    dangerous = Plan(
        goal="danger",
        assumptions=[],
        steps=[
            PlanStep(
                id=1,
                type="shell",
                description="danger",
                command="rm -rf /tmp/x",
                verify=VerifySpec(type="exit_code", target="command", expect="0"),
            )
        ],
    )
    critic = deterministic_critic(dangerous)
    assert critic.ok is False
    assert critic.patched_plan is not None
    assert critic.patched_plan.steps[0].type == "python"


def test_tool_adapter_blocks_destructive_commands() -> None:
    adapter = SecureToolAdapter()
    result = adapter.run_shell("rm -rf /tmp/test")
    assert result.ok is False
    assert "blockerat" in result.error
