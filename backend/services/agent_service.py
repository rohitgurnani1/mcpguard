from typing import List

from backend.attacks.presets import ATTACK_PRESETS
from backend.agent.mock_agent import propose_tool_call
from backend.database import get_audit_log, get_stats, log_decision, update_approval
from backend.models import (
    AgentRunResponse,
    ApprovalActionResponse,
    ApprovalStatus,
    BulkAttackResult,
    Decision,
    PolicySummary,
    ProposedToolCall,
    SecurityDecision,
    StatsSummary,
)
from backend.security.middleware import SecurityMiddleware
from backend.security.policy_engine import PolicyEngine
from backend.tools.mock_tools import execute_tool

_security = SecurityMiddleware()


def get_security_middleware() -> SecurityMiddleware:
    return _security


def run_agent(prompt: str) -> AgentRunResponse:
    tool_call = propose_tool_call(prompt)
    security_decision = _security.evaluate(tool_call)

    executed = False
    tool_result = None
    approval_status = ApprovalStatus.NOT_APPLICABLE

    if security_decision.decision == Decision.ALLOW:
        tool_result = execute_tool(tool_call)
        executed = True
    elif security_decision.decision == Decision.APPROVAL_REQUIRED:
        approval_status = ApprovalStatus.PENDING

    audit_id = log_decision(
        prompt, tool_call, security_decision, executed=executed
    )

    return AgentRunResponse(
        audit_id=audit_id,
        prompt=prompt,
        proposed_tool_call=tool_call,
        security_decision=security_decision,
        approval_status=approval_status,
        tool_result=tool_result,
    )


def approve_action(audit_id: int) -> ApprovalActionResponse:
    entry = _require_pending_approval(audit_id)
    tool_call = ProposedToolCall(tool_name=entry.tool_name, args=entry.tool_args)
    tool_result = execute_tool(tool_call)
    update_approval(audit_id, ApprovalStatus.APPROVED, executed=True)

    return ApprovalActionResponse(
        audit_id=audit_id,
        approval_status=ApprovalStatus.APPROVED,
        tool_result=tool_result,
        message="Action approved and executed (simulated).",
    )


def deny_action(audit_id: int) -> ApprovalActionResponse:
    _require_pending_approval(audit_id)
    update_approval(audit_id, ApprovalStatus.DENIED, executed=False)

    return ApprovalActionResponse(
        audit_id=audit_id,
        approval_status=ApprovalStatus.DENIED,
        tool_result=None,
        message="Action denied by human reviewer.",
    )


def _require_pending_approval(audit_id: int):
    entry = get_audit_log(audit_id)
    if not entry:
        raise LookupError(f"Audit entry {audit_id} not found")
    if entry.decision != Decision.APPROVAL_REQUIRED:
        raise ValueError("This audit entry does not require approval")
    if entry.approval_status != ApprovalStatus.PENDING:
        raise ValueError("This action has already been reviewed")
    return entry


def run_all_attacks() -> List[BulkAttackResult]:
    return [
        BulkAttackResult(
            attack_name=preset.attack_name,
            description=preset.description,
            result=run_agent(preset.prompt),
        )
        for preset in ATTACK_PRESETS
    ]


def fetch_stats() -> StatsSummary:
    return get_stats()


def fetch_policies() -> List[PolicySummary]:
    engine = PolicyEngine()
    summaries: List[PolicySummary] = []
    for rule in engine.rules:
        summaries.append(
            PolicySummary(
                name=rule.get("name", "unknown"),
                description=rule.get("description"),
                tool=rule.get("tool", "*"),
                action=Decision(rule["action"]),
                severity=rule.get("severity", "low"),
                risk_score=rule.get("risk_score"),
            )
        )
    return summaries
