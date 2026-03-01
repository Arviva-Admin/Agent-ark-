"""CLI för Arviva-agenten."""

from __future__ import annotations

import argparse

from arviva_agent.orchestrator.orchestrator import Orchestrator


def main() -> int:
    parser = argparse.ArgumentParser(description="Arviva Autonom Agent")
    parser.add_argument("goal", help="Mål i naturligt språk")
    parser.add_argument("--max-iterations", type=int, default=20)
    args = parser.parse_args()

    result = Orchestrator().run(goal=args.goal, max_iterations=args.max_iterations)
    print(f"Status: {result.status} | Steg: {result.completed_steps} | {result.message}")
    return 0 if result.status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
