"""Planner prompt template."""

from __future__ import annotations

from arviva_agent.prompts.system_policy import SYSTEM_POLICY


def build_planner_prompt(goal: str, context_summary: str, integrations_status: dict[str, object]) -> str:
    return (
        f"{SYSTEM_POLICY}\n"
        "ROLE: PLANNER\n"
        "Output STRICT JSON with schema:\n"
        "{\"goal\":str,\"assumptions\":[str],\"steps\":[{\"id\":int,\"type\":\"shell|python|agent_s|superagi\",\"description\":str,\"command\":str,\"agent_s_action\":object|null,\"simulated\":bool,\"verify\":{\"type\":\"stdout_contains|exit_code|http_status|file_exists|custom\",\"target\":str,\"expect\":str}}]}\n"
        f"GOAL: {goal}\n"
        f"CONTEXT_SUMMARY: {context_summary}\n"
        f"INTEGRATIONS_STATUS: {integrations_status}\n"
    )


def build_repair_prompt(raw_text: str) -> str:
    return (
        f"{SYSTEM_POLICY}\n"
        "ROLE: PLANNER_JSON_REPAIR\n"
        "Fix the following into valid JSON that matches the required schema. Return JSON only.\n"
        f"BROKEN_TEXT: {raw_text}\n"
    )
