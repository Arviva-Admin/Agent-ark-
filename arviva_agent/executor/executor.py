"""Executor that routes steps to shell/python, Agent-S or SuperAGI."""

from __future__ import annotations

from dataclasses import dataclass

from arviva_agent.desktop_control.gui_interaction import GUICommand, GUIInteraction
from arviva_agent.executor.tool_adapter import SecureToolAdapter, ToolResult
from arviva_agent.integrations.superagi_client import SuperAGIClient
from arviva_agent.prompts.schemas import PlanStep


@dataclass
class StepExecution:
    step_id: int
    ok: bool
    output: str
    error: str = ""


class Executor:
    def __init__(
        self,
        tools: SecureToolAdapter | None = None,
        gui: GUIInteraction | None = None,
        superagi: SuperAGIClient | None = None,
    ) -> None:
        self.tools = tools or SecureToolAdapter()
        self.gui = gui or GUIInteraction()
        self.superagi = superagi or SuperAGIClient()

    def execute_step(self, step: PlanStep, goal: str = "") -> StepExecution:
        if step.type == "shell":
            command = step.command or "pwd"
            result: ToolResult = self.tools.run_shell(command)
            return StepExecution(step_id=step.id, ok=result.ok, output=result.output, error=result.error)

        if step.type == "python":
            code = step.command or f"print('planner_goal:', {goal!r})"
            result = self.tools.run_python(code)
            return StepExecution(step_id=step.id, ok=result.ok, output=result.output, error=result.error)

        if step.type == "agent_s":
            if step.agent_s_action:
                action = step.agent_s_action.action
                payload = step.agent_s_action.target or step.agent_s_action.text
            else:
                action, payload = "screenshot", ""
            ok, details = self.gui.execute(GUICommand(action=action, payload=payload))
            return StepExecution(step_id=step.id, ok=ok, output=details, error="" if ok else details)

        if step.type == "superagi":
            result = self.superagi.dispatch_workflow(goal=goal or step.description, context={"step": step.description})
            if result.simulated:
                return StepExecution(
                    step_id=step.id,
                    ok=True,
                    output=f"SuperAGI fallback executed: {result.data}",
                    error="",
                )
            return StepExecution(step_id=step.id, ok=result.ok, output=str(result.data), error=result.error)

        return StepExecution(step_id=step.id, ok=False, output="", error=f"Okänt verktyg: {step.type}")
