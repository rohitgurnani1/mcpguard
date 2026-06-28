import type { StatsSummary } from "../types";

interface StatsBarProps {
  stats: StatsSummary | null;
}

export function StatsBar({ stats }: StatsBarProps) {
  if (!stats) return null;

  const items = [
    { label: "Total Events", value: stats.total_events },
    { label: "Blocked", value: stats.blocked, className: "stat-block" },
    { label: "Allowed", value: stats.allowed, className: "stat-allow" },
    { label: "Pending Approval", value: stats.pending_approval, className: "stat-pending" },
    { label: "Avg Risk", value: stats.average_risk_score },
  ];

  return (
    <section className="stats-bar">
      {items.map((item) => (
        <div key={item.label} className={`stat-card ${item.className ?? ""}`}>
          <span className="stat-value">{item.value}</span>
          <span className="stat-label">{item.label}</span>
        </div>
      ))}
    </section>
  );
}
