import type { BulkAttackResult } from "../types";
import { decisionClass, decisionLabel } from "../utils";

interface AttackResultsTableProps {
  results: BulkAttackResult[];
}

export function AttackResultsTable({ results }: AttackResultsTableProps) {
  if (results.length === 0) return null;

  const blocked = results.filter(
    (r) => r.result.security_decision.decision === "block"
  ).length;
  const allowed = results.filter(
    (r) => r.result.security_decision.decision === "allow"
  ).length;
  const pending = results.filter(
    (r) => r.result.security_decision.decision === "approval_required"
  ).length;

  return (
    <section className="card attack-results">
      <div className="card-header">
        <div>
          <h2>Batch Attack Results</h2>
          <p className="subtitle">
            Ran {results.length} presets — {blocked} blocked, {pending} need
            approval, {allowed} allowed
          </p>
        </div>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Attack</th>
              <th>Tool</th>
              <th>Decision</th>
              <th>Risk</th>
              <th>Policy</th>
            </tr>
          </thead>
          <tbody>
            {results.map((row) => (
              <tr key={row.attack_name}>
                <td className="attack-name-cell">
                  {row.attack_name.replace(/_/g, " ")}
                </td>
                <td className="mono">{row.result.proposed_tool_call.tool_name}</td>
                <td>
                  <span
                    className={decisionClass(
                      row.result.security_decision.decision
                    )}
                  >
                    {decisionLabel(row.result.security_decision.decision)}
                  </span>
                </td>
                <td className="mono">{row.result.security_decision.risk_score}</td>
                <td className="mono">
                  {row.result.security_decision.policy_triggered ?? "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
