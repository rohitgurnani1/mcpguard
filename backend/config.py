from pathlib import Path
import os

APP_VERSION = "0.5.0"
APP_NAME = "MCPGuard"

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
POLICIES_PATH = ROOT_DIR / "backend" / "policies" / "default_policies.yaml"
DATABASE_PATH = DATA_DIR / "audit.db"

# Load .env from project root if present (optional for local dev).
_env_file = ROOT_DIR / ".env"
if _env_file.exists():
    for line in _env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
AGENT_MODE = os.getenv("MCPGUARD_AGENT_MODE", "auto").strip().lower()

DATA_DIR.mkdir(parents=True, exist_ok=True)
