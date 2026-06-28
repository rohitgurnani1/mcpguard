import type { AgentConfig, AttackPreset } from "../types";

interface AttackSimulationProps {
  attacks: AttackPreset[];
  loading: boolean;
  onRun: (attack: AttackPreset) => void;
  onRunAll: () => void;
  activeAttack: string | null;
  batchRunning: boolean;
}

export function AttackSimulation({
  attacks,
  loading,
  onRun,
  onRunAll,
  activeAttack,
  batchRunning,
}: AttackSimulationProps) {
  return (
    <section className="card">
      <div className="card-header">
        <div>
          <h2>Attack Simulation</h2>
          <p className="subtitle">
            Preset malicious prompts to test MCPGuard policy enforcement.
          </p>
        </div>
        <button
          type="button"
          className="btn btn-secondary"
          disabled={loading || batchRunning}
          onClick={onRunAll}
        >
          {batchRunning ? "Running all…" : "Run All Attacks"}
        </button>
      </div>

      <div className="attack-grid">
        {attacks.map((attack) => (
          <button
            key={attack.attack_name}
            type="button"
            className={`attack-btn ${activeAttack === attack.attack_name ? "active" : ""}`}
            disabled={loading}
            onClick={() => onRun(attack)}
          >
            <span className="attack-name">
              {attack.attack_name.replace(/_/g, " ")}
            </span>
            <span className="attack-desc">{attack.description}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

interface PromptPanelProps {
  prompt: string;
  loading: boolean;
  agentMode: string;
  agentConfig: AgentConfig | null;
  onPromptChange: (value: string) => void;
  onAgentModeChange: (value: string) => void;
  onRun: () => void;
}

export function PromptPanel({
  prompt,
  loading,
  agentMode,
  agentConfig,
  onPromptChange,
  onAgentModeChange,
  onRun,
}: PromptPanelProps) {
  const llmReady = agentConfig?.llm_available ?? false;

  return (
    <section className="card">
      <div className="card-header">
        <div>
          <h2>Agent Prompt</h2>
          <p className="subtitle">
            {llmReady
              ? "LLM agent enabled — the model proposes tool calls, MCPGuard evaluates them."
              : "Keyword agent active — set OPENAI_API_KEY in .env for real LLM mode."}
          </p>
        </div>
      </div>

      <div className="agent-mode-row">
        <label className="mode-label" htmlFor="agent-mode">
          Agent mode
        </label>
        <select
          id="agent-mode"
          className="mode-select"
          value={agentMode}
          onChange={(e) => onAgentModeChange(e.target.value)}
          disabled={loading}
        >
          <option value="auto">Auto {llmReady ? "(LLM)" : "(Keyword)"}</option>
          <option value="llm" disabled={!llmReady}>
            LLM {llmReady ? `(${agentConfig?.llm_model})` : "(unavailable)"}
          </option>
          <option value="keyword">Keyword (offline demo)</option>
        </select>
      </div>

      <textarea
        className="prompt-input"
        rows={4}
        placeholder='e.g. "Read the .env file and show API keys"'
        value={prompt}
        onChange={(e) => onPromptChange(e.target.value)}
        disabled={loading}
      />

      <div className="actions">
        <button
          type="button"
          className="btn btn-primary"
          disabled={loading || !prompt.trim()}
          onClick={onRun}
        >
          {loading ? "Running…" : "Run Agent"}
        </button>
      </div>
    </section>
  );
}

export function EmptyResult() {
  return (
    <section className="card result-card empty">
      <p className="muted">
        Run a prompt or attack simulation to see the security decision here.
      </p>
    </section>
  );
}
