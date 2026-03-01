# Arviva Autonomous Agent Platform

En autonom AI-agentplattform för Arviva OS med **faktiska integrationspunkter** mot två open-source ramverk:
- **Agent-S** (GUI/OS-interaktion): https://github.com/simular-ai/Agent-S
- **SuperAGI** (orkestrering/workflows): https://github.com/TransformerOptimus/SuperAGI

## Arkitektur
- `planner/`: naturligt språk -> strukturerad JSON-plan
- `executor/`: kör steg via `shell`, `python`, `agent_s`, `superagi`
- `integrations/agent_s_client.py`: adapter mot lokal Agent-S-repo
- `integrations/superagi_client.py`: HTTP-adapter mot SuperAGI
- `validator/`: verifiering + feedback/replan
- `memory/`: JSONL-logg + semantisk recall
- `orchestrator/`: plan -> execute -> verify -> feedback-loop
- `api/`: FastAPI endpoints `/api/agent/run` och `/api/agent/status`
- `frontend/nextjs_app`: enkel UI för mål och status

## Installation av ramverk (verklig integration)
```bash
./scripts/setup_frameworks.sh
```
Klonar ramverken till `third_party/Agent-S` och `third_party/SuperAGI`.

## Körning
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip fastapi uvicorn pytest pydantic requests
python main.py "Automatisera GUI-arbetsflöde och verifiera resultat"
uvicorn arviva_agent.api.main:app --reload --port 8000
```

## Prompt Stack
Agenten använder en robust prompt-stack:
- **SYSTEM_POLICY**: guardrails, tool-policy, sekretess och destruktiva kommandon blockeras.
- **PLANNER**: returnerar strikt JSON-plan med tool-typed steg och verifiering per steg.
- **CRITIC**: riskbedömer planen och applicerar deterministiska fixar (t.ex. ersätter destruktiva kommandon).

### Exempel på plan-JSON
```json
{
  "goal": "Automatisera deployment",
  "assumptions": ["Agent-S kan vara simulerad"],
  "steps": [
    {
      "id": 1,
      "type": "shell",
      "description": "Verifiera arbetskatalog",
      "command": "pwd",
      "agent_s_action": null,
      "simulated": false,
      "verify": {"type": "exit_code", "target": "command", "expect": "0"}
    }
  ]
}
```

### Simulation och fallback
Om Agent-S eller SuperAGI är otillgängliga planerar/markerar systemet `simulated` och använder fallback till shell/python där möjligt.

## API
- `POST /api/agent/run` kör ett mål och returnerar `{status, details}`.
- `GET /api/agent/status` returnerar `{agent_s, superagi}` med `reachable/mode/url` enligt kontrakt.


## OpenAPI-kontrakt
Den formella API-specifikationen finns i `openapi.yaml` och matchar endpoints:
- `GET /api/agent/status`
- `POST /api/agent/run`

## Hur integrationen fungerar
- **Agent-S** ansvarar för fysisk GUI-interaktion (klick, typing, screenshot) via `AgentSClient` -> `AgentSWrapper` -> `GUIInteraction`.
- **SuperAGI** används som orkestreringslager via `SuperAGIClient.dispatch_workflow` för workflow-dispatch och verktygskoordination.
- **Executor** routar plansteg dynamiskt till rätt verktyg beroende på `step.tool`.
- **Orchestrator** hanterar verifiering, retry/replan och persistens i minnet.

## Exempelworkflows
1. **Build & release**
   - Goal: "Orkestrera byggkedja med SuperAGI, verifiera artefakter, rapportera status".
2. **GUI automation**
   - Goal: "Använd Agent-S för att öppna app, klicka meny, fylla textfält och ta screenshot".

## Felhantering
- allowlist/denylist i `SecureToolAdapter`
- timeout/felklassificering för externa anrop
- verifiering efter varje steg
- retry -> replan policy
- fallback/simulerat läge för Agent-S/SuperAGI när externa beroenden saknas
- körloggar i `data/agent_history.jsonl`
