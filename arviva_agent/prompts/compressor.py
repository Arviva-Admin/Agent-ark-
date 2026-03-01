"""Context compression utilities."""

from __future__ import annotations

from typing import Any


def compress_events(events: list[dict[str, Any]], limit: int = 6, max_chars: int = 1200) -> str:
    recent = events[-limit:]
    lines: list[str] = []
    for event in recent:
        payload = event.get("payload", {})
        step_id = payload.get("step_id") or payload.get("step", {}).get("id")
        execution = payload.get("execution", {})
        result_ok = execution.get("ok")
        output = str(execution.get("output", ""))[:120]
        simulated = "simulated" in str(payload).lower()
        lines.append(
            f"event={event.get('event_type')} step={step_id} ok={result_ok} simulated={simulated} output={output}"
        )
    summary = " | ".join(lines)
    return summary[:max_chars]
