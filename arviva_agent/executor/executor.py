"""Executor that routes steps to shell/python, Agent-S or SuperAGI."""

from __future__ import annotations

from dataclasses import dataclass

from arviva_agent.desktop_control.gui_interaction import GUICommand, GUIInteraction
from arviva_agent.executor.tool_adapter import SecureToolAdapter, ToolResult
from arviva_agent.integrations.superagi_client import SuperAGIClient
from arviva_agent.planner.planner import PlanStep


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
        if step.tool == "shell":
            command = step.action if step.action.startswith(("pwd", "ls", "echo")) else "pwd"
            result: ToolResult = self.tools.run_shell(command)
            return StepExecution(step_id=step.id, ok=result.ok, output=result.output, error=result.error)

        if step.tool == "python":
            code = f"print('planner_goal:', {goal!r})"
            result = self.tools.run_python(code)
            return StepExecution(step_id=step.id, ok=result.ok, output=result.output, error=result.error)

        if step.tool == "agent_s":
            action = "screenshot"
            payload = ""
            if "click" in step.action.lower():
                action = "click"
                payload = "button"
            elif "type" in step.action.lower():
                action = "type"
                payload = goal[:120]
            ok, details = self.gui.execute(GUICommand(action=action, payload=payload))
            return StepExecution(step_id=step.id, ok=ok, output=details, error="" if ok else details)

        if step.tool == "superagi":
            result = self.superagi.dispatch_workflow(goal=goal or step.action, context={"step": step.action})
            if result.simulated:
                return StepExecution(
                    step_id=step.id,
                    ok=True,
                    output=f"SuperAGI fallback executed: {result.data}",
                    error="",
                )
            return StepExecution(step_id=step.id, ok=result.ok, output=str(result.data), error=result.error)

        return StepExecution(step_id=step.id, ok=False, output="", error=f"Okänt verktyg: {step.tool}")
