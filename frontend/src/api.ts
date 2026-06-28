import type {
  AgentRunResponse,
  ApprovalActionResponse,
  AttackPreset,
  AuditLogEntry,
  PolicySummary,
  StatsSummary,
} from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const body = await response.json();
      message = body.detail ?? message;
    } catch {
      const text = await response.text();
      if (text) message = text;
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function runAgent(prompt: string): Promise<AgentRunResponse> {
  return request("/agent/run", {
    method: "POST",
    body: JSON.stringify({ prompt }),
  });
}

export function approveAction(auditId: number): Promise<ApprovalActionResponse> {
  return request(`/agent/approve/${auditId}`, { method: "POST" });
}

export function denyAction(auditId: number): Promise<ApprovalActionResponse> {
  return request(`/agent/deny/${auditId}`, { method: "POST" });
}

export function simulateAttack(
  attackName: string,
  prompt: string
): Promise<AgentRunResponse> {
  return request("/simulate/attack", {
    method: "POST",
    body: JSON.stringify({ attack_name: attackName, prompt }),
  });
}

export function fetchAttacks(): Promise<AttackPreset[]> {
  return request("/simulate/attacks");
}

export function fetchAuditLogs(): Promise<AuditLogEntry[]> {
  return request("/audit/logs");
}

export function fetchStats(): Promise<StatsSummary> {
  return request("/audit/stats");
}

export function fetchPolicies(): Promise<PolicySummary[]> {
  return request("/policies");
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
