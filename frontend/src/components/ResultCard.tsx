import type { AgentRunResponse } from "../types";
import { decisionClass, decisionLabel, riskClass } from "../utils";

interface ResultCardProps {
  result: AgentRunResponse;
  loading: boolean;
  onApprove: () => void;
  onDeny: () => void;
}

export function ResultCard({
  result,
  loading,
  onApprove,
  onDeny,
}: ResultCardProps) {
  const { proposed_tool_call, security_decision, tool_result, approval_status } =
    result;
  const decision = security_decision.decision;
  const pending = approval_status === "pending";

  return (
    <section className="card result-card">
      <div className="card-header">
        <h2>Security Decision</h2>
        <span className={decisionClass(decision)}>
          {decisionLabel(decision)}
        </span>
      </div>

      <div className="result-grid">
        <div className="result-item">
          <span className="label">Audit ID</span>
          <code className="value mono">#{result.audit_id}</code>
        </div>

        <div className="result-item">
          <span className="label">Proposed Tool</span>
          <code className="value mono">{proposed_tool_call.tool_name}</code>
        </div>

        <div className="result-item">
          <span className="label">Risk Score</span>
          <div className="risk-display">
            <span
              className={`risk-score ${riskClass(security_decision.risk_score)}`}
            >
              {security_decision.risk_score}
            </span>
            <div className="risk-bar">
              <div
                className={`risk-bar-fill ${riskClass(security_decision.risk_score)}`}
                style={{ width: `${security_decision.risk_score}%` }}
              />
            </div>
          </div>
        </div>

        <div className="result-item full-width">
          <span className="label">Arguments</span>
          <pre className="code-block">
            {JSON.stringify(proposed_tool_call.args, null, 2)}
          </pre>
        </div>

        <div className="result-item full-width">
          <span className="label">Reason</span>
          <p className="value">{security_decision.reason}</p>
        </div>

        <div className="result-item">
          <span className="label">Policy Triggered</span>
          <code className="value mono">
            {security_decision.policy_triggered ?? "—"}
          </code>
        </div>

        {pending && (
          <div className="result-item full-width approval-actions">
            <span className="label">Human Review Required</span>
            <div className="actions">
              <button
                type="button"
                className="btn btn-approve"
                disabled={loading}
                onClick={onApprove}
              >
                Approve & Execute
              </button>
              <button
                type="button"
                className="btn btn-deny"
                disabled={loading}
                onClick={onDeny}
              >
                Deny
              </button>
            </div>
          </div>
        )}

        <div className="result-item full-width">
          <span className="label">Tool Result</span>
          {tool_result ? (
            <pre className="code-block">{JSON.stringify(tool_result, null, 2)}</pre>
          ) : (
            <p className="value muted">
              {pending
                ? "Awaiting human approval before execution."
                : "Not executed — blocked or denied."}
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
