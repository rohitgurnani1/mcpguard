from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Decision(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    APPROVAL_REQUIRED = "approval_required"


class ApprovalStatus(str, Enum):
    NOT_APPLICABLE = "not_applicable"
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


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
    audit_id: int
    prompt: str
    proposed_tool_call: ProposedToolCall
    security_decision: SecurityDecision
    approval_status: ApprovalStatus = ApprovalStatus.NOT_APPLICABLE
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
    executed: bool = False
    approval_status: ApprovalStatus = ApprovalStatus.NOT_APPLICABLE


class SimulateAttackRequest(BaseModel):
    attack_name: str
    prompt: str


class AttackPreset(BaseModel):
    attack_name: str
    description: str
    prompt: str


class PolicySummary(BaseModel):
    name: str
    description: Optional[str] = None
    tool: str
    action: Decision
    severity: str
    risk_score: Optional[int] = None


class StatsSummary(BaseModel):
    total_events: int
    allowed: int
    blocked: int
    pending_approval: int
    executed: int
    average_risk_score: float


class ApprovalActionResponse(BaseModel):
    audit_id: int
    approval_status: ApprovalStatus
    tool_result: Optional[Dict[str, Any]] = None
    message: str


class BulkAttackResult(BaseModel):
    attack_name: str
    description: str
    result: AgentRunResponse
