export type Decision = "allow" | "block" | "approval_required";

export type ApprovalStatus =
  | "not_applicable"
  | "pending"
  | "approved"
  | "denied";

export interface ProposedToolCall {
  tool_name: string;
  args: Record<string, unknown>;
}

export interface SecurityDecision {
  decision: Decision;
  risk_score: number;
  reason: string;
  policy_triggered: string | null;
}

export interface AgentRunResponse {
  audit_id: number;
  prompt: string;
  proposed_tool_call: ProposedToolCall;
  security_decision: SecurityDecision;
  approval_status: ApprovalStatus;
  tool_result: Record<string, unknown> | null;
}

export interface AttackPreset {
  attack_name: string;
  description: string;
  prompt: string;
}

export interface AuditLogEntry {
  id: number;
  timestamp: string;
  prompt: string;
  tool_name: string;
  tool_args: Record<string, unknown>;
  decision: Decision;
  risk_score: number;
  reason: string;
  policy_triggered: string | null;
  executed: boolean;
  approval_status: ApprovalStatus;
}

export interface StatsSummary {
  total_events: number;
  allowed: number;
  blocked: number;
  pending_approval: number;
  executed: number;
  average_risk_score: number;
}

export interface PolicySummary {
  name: string;
  description?: string;
  tool: string;
  action: Decision;
  severity: string;
  risk_score?: number;
}

export interface ApprovalActionResponse {
  audit_id: number;
  approval_status: ApprovalStatus;
  tool_result: Record<string, unknown> | null;
  message: string;
}

export interface BulkAttackResult {
  attack_name: string;
  description: string;
  result: AgentRunResponse;
}
