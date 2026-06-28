import type { AuditLogEntry } from "../types";
import { decisionClass, decisionLabel, formatTimestamp, truncate } from "../utils";

interface AuditTableProps {
  logs: AuditLogEntry[];
  loading: boolean;
  onRefresh: () => void;
}

export function AuditTable({ logs, loading, onRefresh }: AuditTableProps) {
  return (
    <section className="card audit-card">
      <div className="card-header">
        <div>
          <h2>Audit Logs</h2>
          <p className="subtitle">
            Every tool-call decision is persisted to SQLite.
          </p>
        </div>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={onRefresh}
          disabled={loading}
        >
          Refresh
        </button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Prompt</th>
              <th>Tool</th>
              <th>Decision</th>
              <th>Risk</th>
              <th>Policy</th>
              <th>Reason</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan={7} className="empty-row">
                  No audit entries yet.
                </td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log.id}>
                  <td className="mono nowrap">{formatTimestamp(log.timestamp)}</td>
                  <td title={log.prompt}>{truncate(log.prompt, 60)}</td>
                  <td className="mono">{log.tool_name}</td>
                  <td>
                    <span className={decisionClass(log.decision)}>
                      {decisionLabel(log.decision)}
                    </span>
                  </td>
                  <td className="mono">{log.risk_score}</td>
                  <td className="mono">{log.policy_triggered ?? "—"}</td>
                  <td title={log.reason}>{truncate(log.reason, 50)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
