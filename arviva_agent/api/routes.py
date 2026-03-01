"""FastAPI routes för agentkontroll."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from arviva_agent.integrations.agent_s_client import AgentSClient
from arviva_agent.integrations.superagi_client import SuperAGIClient
from arviva_agent.orchestrator.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()


class RunRequest(BaseModel):
    goal: str = Field(..., min_length=1, description="Mål i naturligt språk")
    max_iterations: int = Field(10, ge=1, le=100, description="Max antal iterationer")


class RunResponse(BaseModel):
    status: str
    details: dict[str, Any]


class AgentStatusResponse(BaseModel):
    agent_s: dict[str, Any]
    superagi: dict[str, Any]


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/agent/status", response_model=AgentStatusResponse, tags=["Agent Status"])
def agent_status() -> AgentStatusResponse:
    superagi_client = SuperAGIClient()
    superagi_health = superagi_client.health()
    agent_s_reachable = AgentSClient().is_available()

    return AgentStatusResponse(
        agent_s={
            "reachable": agent_s_reachable,
            "mode": "real" if agent_s_reachable else "simulated",
        },
        superagi={
            "reachable": superagi_health.ok,
            "mode": "real" if superagi_health.ok else "simulated",
            "url": superagi_client.base_url,
        },
    )


@router.post("/agent/run", response_model=RunResponse, tags=["Agent Control"])
def run_agent(request: RunRequest) -> RunResponse:
    """Kör agentloop för ett mål och returnerar strukturerat resultat."""
    try:
        superagi_client = SuperAGIClient()
        superagi_health = superagi_client.health()
        integrations_status = {
            "agent_s": {
                "reachable": AgentSClient().is_available(),
                "mode": "real" if AgentSClient().is_available() else "simulated",
            },
            "superagi": {
                "reachable": superagi_health.ok,
                "mode": "real" if superagi_health.ok else "simulated",
                "url": superagi_client.base_url,
            },
        }
        result = orchestrator.run(
            goal=request.goal,
            max_iterations=request.max_iterations,
            integrations_status=integrations_status,
        )
        return RunResponse(
            status="success" if result.status == "completed" else result.status,
            details={
                "orchestrator_status": result.status,
                "completed_steps": result.completed_steps,
                "message": result.message,
                "goal": request.goal,
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Server-fel under agentkörning: {exc}") from exc
