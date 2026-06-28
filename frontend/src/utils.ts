import type { Decision } from "./types";

export function decisionLabel(decision: Decision): string {
  switch (decision) {
    case "allow":
      return "Allow";
    case "block":
      return "Block";
    case "approval_required":
      return "Approval Required";
    default:
      return decision;
  }
}

export function decisionClass(decision: Decision): string {
  return `badge badge-${decision}`;
}

export function riskClass(score: number): string {
  if (score >= 90) return "risk-critical";
  if (score >= 50) return "risk-medium";
  if (score >= 25) return "risk-low";
  return "risk-safe";
}

export function formatTimestamp(iso: string): string {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export function truncate(text: string, max = 80): string {
  if (text.length <= max) return text;
  return `${text.slice(0, max)}…`;
}
