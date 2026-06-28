from typing import List

from fastapi import APIRouter, HTTPException

from backend.attacks.presets import ATTACK_PRESETS
from backend.config import APP_NAME, APP_VERSION
from backend.database import get_audit_logs
from backend.models import (
    AgentRunRequest,
    AgentRunResponse,
    AgentConfig,
    ApprovalActionResponse,
    AttackPreset,
    AuditLogEntry,
    BulkAttackResult,
    PolicySummary,
    SimulateAttackRequest,
    StatsSummary,
)
from backend.agent.proposer import get_agent_config
from backend.services.agent_service import (
    approve_action,
    deny_action,
    fetch_policies,
    fetch_stats,
    run_agent,
    run_all_attacks,
)

router = APIRouter()


@router.get("/health")
def health() -> dict:
    config = get_agent_config()
    return {
        "status": "ok",
        "service": APP_NAME,
        "version": APP_VERSION,
        "agent_mode": config["active_mode"],
        "llm_available": config["llm_available"],
    }


@router.get("/agent/config", response_model=AgentConfig)
def agent_config() -> AgentConfig:
    return AgentConfig(**get_agent_config())


@router.post("/agent/run", response_model=AgentRunResponse)
def agent_run(request: AgentRunRequest) -> AgentRunResponse:
    return run_agent(request.prompt, request.agent_mode)


@router.post("/agent/approve/{audit_id}", response_model=ApprovalActionResponse)
def agent_approve(audit_id: int) -> ApprovalActionResponse:
    try:
        return approve_action(audit_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/agent/deny/{audit_id}", response_model=ApprovalActionResponse)
def agent_deny(audit_id: int) -> ApprovalActionResponse:
    try:
        return deny_action(audit_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/audit/logs", response_model=List[AuditLogEntry])
def audit_logs(limit: int = 500) -> List[AuditLogEntry]:
    return get_audit_logs(limit=limit)


@router.get("/audit/stats", response_model=StatsSummary)
def audit_stats() -> StatsSummary:
    return fetch_stats()


@router.get("/policies", response_model=List[PolicySummary])
def list_policies() -> List[PolicySummary]:
    return fetch_policies()


@router.get("/simulate/attacks", response_model=List[AttackPreset])
def list_attacks() -> List[AttackPreset]:
    return ATTACK_PRESETS


@router.post("/simulate/attack", response_model=AgentRunResponse)
def simulate_attack(request: SimulateAttackRequest) -> AgentRunResponse:
    return run_agent(request.prompt)


@router.post("/simulate/attacks/run-all", response_model=List[BulkAttackResult])
def simulate_all_attacks() -> List[BulkAttackResult]:
    return run_all_attacks()
