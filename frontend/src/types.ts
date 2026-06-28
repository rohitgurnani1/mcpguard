export type Decision = "allow" | "block" | "approval_required";

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
  prompt: string;
  proposed_tool_call: ProposedToolCall;
  security_decision: SecurityDecision;
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
}
