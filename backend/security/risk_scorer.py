from backend.models import Decision


def score_decision(decision: Decision, severity: str, policy_name: str) -> int:
    """
    Fallback risk scoring when a rule omits an explicit risk_score.

    Ranges:
      - critical blocked actions: 90-100
      - approval actions: 50-75
      - suspicious but allowed: 25-50
      - normal allowed: 0-20
    """
    if decision == Decision.BLOCK:
        return _score_blocked(severity, policy_name)

    if decision == Decision.APPROVAL_REQUIRED:
        return _score_approval(severity, policy_name)

    if severity in ("suspicious", "medium"):
        return _score_suspicious(policy_name)

    return _score_normal(policy_name)


def _score_blocked(severity: str, policy_name: str) -> int:
    base = 95 if severity == "critical" else 90
    return min(100, base + _hash_offset(policy_name, 5))


def _score_approval(severity: str, policy_name: str) -> int:
    base = 65 if severity == "medium" else 55
    return min(75, base + _hash_offset(policy_name, 10))


def _score_suspicious(policy_name: str) -> int:
    return min(50, 30 + _hash_offset(policy_name, 20))


def _score_normal(policy_name: str) -> int:
    return min(20, 5 + _hash_offset(policy_name, 15))


def _hash_offset(value: str, span: int) -> int:
    return sum(ord(c) for c in value) % span
