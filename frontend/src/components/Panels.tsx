import type { AttackPreset } from "../types";

interface AttackSimulationProps {
  attacks: AttackPreset[];
  loading: boolean;
  onRun: (attack: AttackPreset) => void;
  activeAttack: string | null;
}

export function AttackSimulation({
  attacks,
  loading,
  onRun,
  activeAttack,
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
  onPromptChange: (value: string) => void;
  onRun: () => void;
}

export function PromptPanel({
  prompt,
  loading,
  onPromptChange,
  onRun,
}: PromptPanelProps) {
  return (
    <section className="card">
      <div className="card-header">
        <div>
          <h2>Agent Prompt</h2>
          <p className="subtitle">
            Enter a prompt — the mock agent proposes a tool call, then MCPGuard
            evaluates it.
          </p>
        </div>
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
