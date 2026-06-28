from typing import Any, Dict

from backend.models import ProposedToolCall


def execute_tool(tool_call: ProposedToolCall) -> Dict[str, Any]:
    """Simulate tool execution — no real side effects in MVP."""
    handlers = {
        "read_file": _read_file,
        "send_email": _send_email,
        "run_shell_command": _run_shell_command,
        "query_database": _query_database,
        "search_web": _search_web,
    }

    handler = handlers.get(tool_call.tool_name)
    if not handler:
        return {"status": "error", "message": f"Unknown tool: {tool_call.tool_name}"}

    return handler(tool_call.args)


def _read_file(args: Dict[str, Any]) -> Dict[str, Any]:
    path = args.get("path", "")
    return {
        "status": "simulated",
        "tool": "read_file",
        "path": path,
        "content": f"[SIMULATED] Contents of {path}",
    }


def _send_email(args: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "simulated",
        "tool": "send_email",
        "to": args.get("to"),
        "subject": args.get("subject"),
        "body": args.get("body"),
        "message": "Email was not actually sent (MVP simulation).",
    }


def _run_shell_command(args: Dict[str, Any]) -> Dict[str, Any]:
    command = args.get("command", "")
    return {
        "status": "simulated",
        "tool": "run_shell_command",
        "command": command,
        "stdout": f"[SIMULATED] Output of: {command}",
        "exit_code": 0,
    }


def _query_database(args: Dict[str, Any]) -> Dict[str, Any]:
    query = args.get("query", "")
    return {
        "status": "simulated",
        "tool": "query_database",
        "query": query,
        "rows": [{"id": 1, "name": "sample_row"}],
    }


def _search_web(args: Dict[str, Any]) -> Dict[str, Any]:
    query = args.get("query", "")
    return {
        "status": "simulated",
        "tool": "search_web",
        "query": query,
        "results": [
            {"title": f"Result for '{query}'", "url": "https://example.com/1"},
        ],
    }
