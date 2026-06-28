import type { AgentRunResponse } from "../types";
import { decisionClass, decisionLabel, riskClass } from "../utils";

interface ResultCardProps {
  result: AgentRunResponse;
}

export function ResultCard({ result }: ResultCardProps) {
  const { proposed_tool_call, security_decision, tool_result } = result;
  const decision = security_decision.decision;

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

        <div className="result-item full-width">
          <span className="label">Tool Result</span>
          {tool_result ? (
            <pre className="code-block">{JSON.stringify(tool_result, null, 2)}</pre>
          ) : (
            <p className="value muted">
              Not executed — blocked or pending approval.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
