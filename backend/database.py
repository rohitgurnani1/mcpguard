import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import List, Optional

from backend.config import DATABASE_PATH
from backend.models import (
    ApprovalStatus,
    AuditLogEntry,
    Decision,
    ProposedToolCall,
    SecurityDecision,
    StatsSummary,
)


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
                policy_triggered TEXT,
                executed INTEGER NOT NULL DEFAULT 0,
                approval_status TEXT NOT NULL DEFAULT 'not_applicable'
            )
            """
        )
        _migrate_schema(conn)
        conn.commit()


def _migrate_schema(conn: sqlite3.Connection) -> None:
    columns = {row[1] for row in conn.execute("PRAGMA table_info(audit_logs)")}
    if "executed" not in columns:
        conn.execute(
            "ALTER TABLE audit_logs ADD COLUMN executed INTEGER NOT NULL DEFAULT 0"
        )
    if "approval_status" not in columns:
        conn.execute(
            """
            ALTER TABLE audit_logs
            ADD COLUMN approval_status TEXT NOT NULL DEFAULT 'not_applicable'
            """
        )


@contextmanager
def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _approval_status_for(decision: Decision) -> ApprovalStatus:
    if decision == Decision.APPROVAL_REQUIRED:
        return ApprovalStatus.PENDING
    return ApprovalStatus.NOT_APPLICABLE


def log_decision(
    prompt: str,
    tool_call: ProposedToolCall,
    security: SecurityDecision,
    executed: bool = False,
) -> int:
    approval_status = _approval_status_for(security.decision)
    if security.decision == Decision.ALLOW and executed:
        approval_status = ApprovalStatus.NOT_APPLICABLE

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO audit_logs (
                timestamp, prompt, tool_name, tool_args,
                decision, risk_score, reason, policy_triggered,
                executed, approval_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                int(executed),
                approval_status.value,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def get_audit_log(audit_id: int) -> Optional[AuditLogEntry]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM audit_logs WHERE id = ?",
            (audit_id,),
        ).fetchone()
    if not row:
        return None
    return _row_to_entry(row)


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
    return [_row_to_entry(row) for row in rows]


def update_approval(
    audit_id: int,
    approval_status: ApprovalStatus,
    executed: bool,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE audit_logs
            SET approval_status = ?, executed = ?
            WHERE id = ?
            """,
            (approval_status.value, int(executed), audit_id),
        )
        conn.commit()


def get_stats() -> StatsSummary:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN decision = 'allow' THEN 1 ELSE 0 END) AS allowed,
                SUM(CASE WHEN decision = 'block' THEN 1 ELSE 0 END) AS blocked,
                SUM(CASE WHEN approval_status = 'pending' THEN 1 ELSE 0 END) AS pending,
                SUM(CASE WHEN executed = 1 THEN 1 ELSE 0 END) AS executed,
                AVG(risk_score) AS avg_risk
            FROM audit_logs
            """
        ).fetchone()

    return StatsSummary(
        total_events=int(row["total"] or 0),
        allowed=int(row["allowed"] or 0),
        blocked=int(row["blocked"] or 0),
        pending_approval=int(row["pending"] or 0),
        executed=int(row["executed"] or 0),
        average_risk_score=round(float(row["avg_risk"] or 0), 1),
    )


def _row_to_entry(row: sqlite3.Row) -> AuditLogEntry:
    return AuditLogEntry(
        id=row["id"],
        timestamp=row["timestamp"],
        prompt=row["prompt"],
        tool_name=row["tool_name"],
        tool_args=json.loads(row["tool_args"]),
        decision=Decision(row["decision"]),
        risk_score=row["risk_score"],
        reason=row["reason"],
        policy_triggered=row["policy_triggered"],
        executed=bool(row["executed"]),
        approval_status=ApprovalStatus(row["approval_status"]),
    )
