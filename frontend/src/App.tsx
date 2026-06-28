import { useCallback, useEffect, useState } from "react";
import {
  approveAction,
  checkHealth,
  denyAction,
  fetchAttacks,
  fetchAuditLogs,
  fetchStats,
  runAgent,
  runAllAttacks,
  simulateAttack,
} from "./api";
import { AttackResultsTable } from "./components/AttackResultsTable";
import { AuditTable } from "./components/AuditTable";
import {
  AttackSimulation,
  EmptyResult,
  PromptPanel,
} from "./components/Panels";
import { ResultCard } from "./components/ResultCard";
import { StatsBar } from "./components/StatsBar";
import type {
  AgentRunResponse,
  ApprovalActionResponse,
  AttackPreset,
  AuditLogEntry,
  BulkAttackResult,
  StatsSummary,
} from "./types";

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState<AgentRunResponse | null>(null);
  const [attacks, setAttacks] = useState<AttackPreset[]>([]);
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [stats, setStats] = useState<StatsSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [logsLoading, setLogsLoading] = useState(false);
  const [activeAttack, setActiveAttack] = useState<string | null>(null);
  const [batchResults, setBatchResults] = useState<BulkAttackResult[]>([]);
  const [batchRunning, setBatchRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [backendOk, setBackendOk] = useState(true);

  const refreshLogs = useCallback(async () => {
    setLogsLoading(true);
    try {
      const [logData, statsData] = await Promise.all([
        fetchAuditLogs(),
        fetchStats(),
      ]);
      setLogs(logData);
      setStats(statsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load audit logs");
    } finally {
      setLogsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth().then(setBackendOk);
    fetchAttacks()
      .then(setAttacks)
      .catch(() => setError("Failed to load attack presets"));
    refreshLogs();
  }, [refreshLogs]);

  async function handleRunAgent() {
    if (!prompt.trim()) return;
    setLoading(true);
    setError(null);
    setActiveAttack(null);
    try {
      const data = await runAgent(prompt.trim());
      setResult(data);
      await refreshLogs();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Agent run failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleRunAttack(attack: AttackPreset) {
    setLoading(true);
    setError(null);
    setActiveAttack(attack.attack_name);
    setPrompt(attack.prompt);
    try {
      const data = await simulateAttack(attack.attack_name, attack.prompt);
      setResult(data);
      await refreshLogs();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Attack simulation failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleRunAllAttacks() {
    setBatchRunning(true);
    setLoading(true);
    setError(null);
    setActiveAttack(null);
    setBatchResults([]);
    try {
      const data = await runAllAttacks();
      setBatchResults(data);
      if (data.length > 0) {
        setResult(data[data.length - 1].result);
        setPrompt(data[data.length - 1].result.prompt);
      }
      await refreshLogs();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Batch attack run failed");
    } finally {
      setBatchRunning(false);
      setLoading(false);
    }
  }

  async function handleApproval(action: "approve" | "deny") {
    if (!result) return;
    setLoading(true);
    setError(null);
    try {
      const response: ApprovalActionResponse =
        action === "approve"
          ? await approveAction(result.audit_id)
          : await denyAction(result.audit_id);

      setResult({
        ...result,
        approval_status: response.approval_status,
        tool_result: response.tool_result,
      });
      await refreshLogs();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Approval action failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="brand">
            <div className="logo" aria-hidden>
              <svg viewBox="0 0 24 24" fill="none">
                <path
                  d="M12 2L4 6v6c0 5 3.5 9.5 8 10 4.5-.5 8-5 8-10V6l-8-4z"
                  stroke="currentColor"
                  strokeWidth="1.5"
                />
                <path
                  d="M9 12l2 2 4-4"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
              </svg>
            </div>
            <div>
              <h1>MCPGuard</h1>
              <p>AI Agent Tool-Call Security Firewall</p>
            </div>
          </div>
          <div className={`status-pill ${backendOk ? "" : "offline"}`}>
            <span className={`status-dot ${backendOk ? "" : "offline"}`} />
            {backendOk ? "Backend connected" : "Backend offline"}
          </div>
        </div>
      </header>

      <main className="main">
        {error && (
          <div className="error-banner" role="alert">
            {error}
          </div>
        )}

        <StatsBar stats={stats} />

        <div className="layout-top">
          <PromptPanel
            prompt={prompt}
            loading={loading}
            onPromptChange={setPrompt}
            onRun={handleRunAgent}
          />
          {result ? (
            <ResultCard
              result={result}
              loading={loading}
              onApprove={() => handleApproval("approve")}
              onDeny={() => handleApproval("deny")}
            />
          ) : (
            <EmptyResult />
          )}
        </div>

        <AttackSimulation
          attacks={attacks}
          loading={loading}
          onRun={handleRunAttack}
          onRunAll={handleRunAllAttacks}
          activeAttack={activeAttack}
          batchRunning={batchRunning}
        />

        <AttackResultsTable results={batchResults} />

        <AuditTable logs={logs} loading={logsLoading} onRefresh={refreshLogs} />
      </main>

      <footer className="footer">
        MCPGuard — YAML policies, human-in-the-loop approval, SQLite audit trail
      </footer>
    </div>
  );
}
