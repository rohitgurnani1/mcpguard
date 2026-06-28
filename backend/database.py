import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from backend.models import AuditLogEntry, Decision, ProposedToolCall, SecurityDecision

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "audit.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                prompt TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                tool_args TEXT NOT NULL,
                decision TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                reason TEXT NOT NULL,
                policy_triggered TEXT
            )
            """
        )
        conn.commit()


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def log_decision(
    prompt: str,
    tool_call: ProposedToolCall,
    security: SecurityDecision,
) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO audit_logs (
                timestamp, prompt, tool_name, tool_args,
                decision, risk_score, reason, policy_triggered
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                prompt,
                tool_call.tool_name,
                json.dumps(tool_call.args),
                security.decision.value,
                security.risk_score,
                security.reason,
                security.policy_triggered,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def get_audit_logs(limit: int = 500) -> List[AuditLogEntry]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM audit_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        AuditLogEntry(
            id=row["id"],
            timestamp=row["timestamp"],
            prompt=row["prompt"],
            tool_name=row["tool_name"],
            tool_args=json.loads(row["tool_args"]),
            decision=Decision(row["decision"]),
            risk_score=row["risk_score"],
            reason=row["reason"],
            policy_triggered=row["policy_triggered"],
        )
        for row in rows
    ]
