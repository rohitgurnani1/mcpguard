import type {
  AgentRunResponse,
  AttackPreset,
  AuditLogEntry,
} from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function runAgent(prompt: string): Promise<AgentRunResponse> {
  return request("/agent/run", {
    method: "POST",
    body: JSON.stringify({ prompt }),
  });
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

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
