from typing import Optional

from backend.models import Decision, ProposedToolCall, SecurityDecision
from backend.security.policy_engine import PolicyEngine
from backend.tools.mock_tools import execute_tool


class SecurityMiddleware:
    """Intercepts proposed tool calls, evaluates policy, and optionally executes."""

    def __init__(self, policy_engine: Optional[PolicyEngine] = None) -> None:
        self.policy_engine = policy_engine or PolicyEngine()

    def evaluate(self, tool_call: ProposedToolCall) -> SecurityDecision:
        return self.policy_engine.evaluate(tool_call)

    def run_if_allowed(
        self, tool_call: ProposedToolCall, security: SecurityDecision
    ):
        if security.decision != Decision.ALLOW:
            return None
        return execute_tool(tool_call)
