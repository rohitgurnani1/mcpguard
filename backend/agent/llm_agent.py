import json
import os
from typing import Optional

from openai import OpenAI

from backend.config import OPENAI_API_KEY, OPENAI_MODEL
from backend.models import ProposedToolCall

ALLOWED_TOOLS = {
    "read_file": {"path"},
    "send_email": {"to", "subject", "body"},
    "run_shell_command": {"command"},
    "query_database": {"query"},
    "search_web": {"query"},
}

SYSTEM_PROMPT = """You are an AI agent that chooses exactly ONE tool to act on a user request.

Available tools:
- read_file: read a file from disk. Args: path (string)
- send_email: send an email. Args: to, subject, body (strings)
- run_shell_command: run a shell command. Args: command (string)
- query_database: run a SQL query. Args: query (string)
- search_web: search the web. Args: query (string)

Respond with ONLY valid JSON in this shape:
{"tool_name": "<tool_name>", "args": {<arg_key>: <arg_value>, ...}}

Pick the single best tool for the user's intent. Include realistic argument values derived from the prompt."""


def is_llm_available() -> bool:
    return bool(OPENAI_API_KEY)


def propose_tool_call_llm(prompt: str) -> ProposedToolCall:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Empty response from LLM")

    data = json.loads(content)
    tool_name = data.get("tool_name", "")
    args = data.get("args", {})

    if tool_name not in ALLOWED_TOOLS:
        raise ValueError(f"LLM returned unknown tool: {tool_name}")

    if not isinstance(args, dict):
        raise ValueError("LLM args must be an object")

    return ProposedToolCall(tool_name=tool_name, args=args)
