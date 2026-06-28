from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from backend.models import Decision, ProposedToolCall, SecurityDecision
from backend.security.risk_scorer import score_decision

POLICIES_PATH = Path(__file__).resolve().parent.parent / "policies" / "default_policies.yaml"


class PolicyEngine:
    def __init__(self, policies_path: Optional[Path] = None) -> None:
        path = policies_path or POLICIES_PATH
        with open(path, encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        # Support both `rules` (preferred) and legacy `policies` key.
        self.rules: List[Dict[str, Any]] = data.get("rules") or data.get("policies", [])

    def evaluate(self, tool_call: ProposedToolCall) -> SecurityDecision:
        matches: List[SecurityDecision] = []

        for rule in self.rules:
            if rule.get("tool") != tool_call.tool_name:
                continue
            if not self._matches(rule, tool_call):
                continue

            decision = Decision(rule["action"])
            policy_name = rule.get("name", "unknown_policy")
            severity = rule.get("severity", "low")
            risk_score = rule.get("risk_score")
            if risk_score is None:
                risk_score = score_decision(decision, severity, policy_name)

            matches.append(
                SecurityDecision(
                    decision=decision,
                    risk_score=int(risk_score),
                    reason=rule.get("reason", "Policy rule triggered"),
                    policy_triggered=policy_name,
                )
            )

        if not matches:
            return SecurityDecision(
                decision=Decision.ALLOW,
                risk_score=score_decision(Decision.ALLOW, "low", "no_policy_match"),
                reason="No policy matched; default allow",
                policy_triggered=None,
            )

        return self._most_restrictive(matches)

    def _matches(self, rule: Dict[str, Any], tool_call: ProposedToolCall) -> bool:
        match_spec = rule.get("match", {})
        arg_name = match_spec.get("arg")

        if match_spec.get("exists") is True:
            if not arg_name:
                return False
            value = tool_call.args.get(arg_name)
            return value is not None and str(value).strip() != ""

        if "contains_any" in match_spec:
            if not arg_name:
                return False
            value = str(tool_call.args.get(arg_name, "")).lower()
            needles = match_spec.get("contains_any", [])
            return any(needle.lower() in value for needle in needles)

        return False

    def _most_restrictive(self, decisions: List[SecurityDecision]) -> SecurityDecision:
        priority = {
            Decision.BLOCK: 3,
            Decision.APPROVAL_REQUIRED: 2,
            Decision.ALLOW: 1,
        }
        decisions.sort(
            key=lambda item: (priority[item.decision], item.risk_score),
            reverse=True,
        )
        return decisions[0]
