import os
from typing import Literal, Optional, Tuple

from backend.agent.llm_agent import is_llm_available, propose_tool_call_llm
from backend.agent.mock_agent import propose_tool_call as propose_tool_call_keyword
from backend.config import AGENT_MODE, OPENAI_MODEL
from backend.models import ProposedToolCall

AgentMode = Literal["llm", "keyword"]


def resolve_agent_mode(requested: str = "auto") -> AgentMode:
    """
    Determine which agent backend to use.

    MCPGUARD_AGENT_MODE env:
      - auto: LLM if OPENAI_API_KEY is set, else keyword
      - llm: force LLM (falls back to keyword if no key)
      - keyword: always keyword matching
    """
    mode = (requested or "auto").lower()
    env_mode = AGENT_MODE.lower()

    if mode == "keyword" or env_mode == "keyword":
        return "keyword"
    if mode == "llm" or env_mode == "llm":
        return "llm" if is_llm_available() else "keyword"
    # auto
    return "llm" if is_llm_available() else "keyword"


def propose_tool_call(
    prompt: str, requested_mode: str = "auto"
) -> Tuple[ProposedToolCall, AgentMode, Optional[str]]:
    mode = resolve_agent_mode(requested_mode)

    if mode == "llm":
        try:
            return propose_tool_call_llm(prompt), "llm", OPENAI_MODEL
        except Exception:
            # Graceful fallback keeps demos working if the API fails.
            return propose_tool_call_keyword(prompt), "keyword", None

    return propose_tool_call_keyword(prompt), "keyword", None


def get_agent_config() -> dict:
    llm_available = is_llm_available()
    active = resolve_agent_mode("auto")
    return {
        "active_mode": active,
        "llm_available": llm_available,
        "llm_model": OPENAI_MODEL if llm_available else None,
        "default_mode": AGENT_MODE,
        "supported_tools": list(
            ["read_file", "send_email", "run_shell_command", "query_database", "search_web"]
        ),
    }
