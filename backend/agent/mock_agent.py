import re
from typing import List

from backend.models import ProposedToolCall


def propose_tool_call(prompt: str) -> ProposedToolCall:
    """Keyword-based mock agent for MVP demos."""
    text = prompt.lower()

    if _matches_any(text, ["email", "send", "exfiltrate"]) or "@" in prompt:
        return _propose_send_email(prompt)

    if _matches_any(text, [".env", "secret", "api key", "private key", "file"]):
        return _propose_read_file(prompt, text)

    if _matches_any(text, ["database", "users", "dump", "drop", "delete", "sql"]):
        return _propose_database_query(prompt, text)

    if _matches_any(
        text,
        ["shell", "command", "delete", "install", "curl", "bash", "sudo", "rm -rf"],
    ):
        return _propose_shell_command(prompt)

    return ProposedToolCall(tool_name="search_web", args={"query": prompt.strip()})


def _matches_any(text: str, keywords: List[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _propose_read_file(prompt: str, text: str) -> ProposedToolCall:
    path_match = re.search(r"[\w./~-]+\.(env|pem|key|rsa|txt)", prompt, re.IGNORECASE)
    if path_match:
        path = path_match.group(0)
    elif ".env" in text:
        path = ".env"
    elif "private key" in text or "id_rsa" in text:
        path = "~/.ssh/id_rsa"
    else:
        path = "/tmp/secrets.txt"
    return ProposedToolCall(tool_name="read_file", args={"path": path})


def _propose_send_email(prompt: str) -> ProposedToolCall:
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", prompt)
    return ProposedToolCall(
        tool_name="send_email",
        args={
            "to": email_match.group(0) if email_match else "target@example.com",
            "subject": "Automated message",
            "body": prompt,
        },
    )


def _propose_shell_command(prompt: str) -> ProposedToolCall:
    command = prompt
    lowered = prompt.lower()
    for prefix in (
        "run shell command:",
        "run command:",
        "execute command ",
        "execute: ",
        "run ",
    ):
        if lowered.startswith(prefix):
            command = prompt[len(prefix) :].strip()
            break
    return ProposedToolCall(tool_name="run_shell_command", args={"command": command})


def _propose_database_query(prompt: str, text: str) -> ProposedToolCall:
    if "dump" in text and "user" in text:
        query = "SELECT * FROM users"
    elif "drop" in text:
        query = "DROP TABLE users"
    elif "delete" in text:
        query = "DELETE FROM users"
    else:
        query = prompt
        for prefix in ("run sql:", "sql query:", "query database ", "run query "):
            if text.startswith(prefix):
                query = prompt[len(prefix) :].strip()
                break
    return ProposedToolCall(tool_name="query_database", args={"query": query})
