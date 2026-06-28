from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Decision(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    APPROVAL_REQUIRED = "approval_required"


class AgentRunRequest(BaseModel):
    prompt: str


class ProposedToolCall(BaseModel):
    tool_name: str
    args: Dict[str, Any]


class SecurityDecision(BaseModel):
    decision: Decision
    risk_score: int = Field(ge=0, le=100)
    reason: str
    policy_triggered: Optional[str] = None


class AgentRunResponse(BaseModel):
    prompt: str
    proposed_tool_call: ProposedToolCall
    security_decision: SecurityDecision
    tool_result: Optional[Dict[str, Any]] = None


class AuditLogEntry(BaseModel):
    id: int
    timestamp: str
    prompt: str
    tool_name: str
    tool_args: Dict[str, Any]
    decision: Decision
    risk_score: int
    reason: str
    policy_triggered: Optional[str] = None


class SimulateAttackRequest(BaseModel):
    attack_name: str
    prompt: str


class AttackPreset(BaseModel):
    attack_name: str
    description: str
    prompt: str
