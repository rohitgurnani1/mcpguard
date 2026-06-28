from pathlib import Path

APP_VERSION = "0.3.0"
APP_NAME = "MCPGuard"

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
POLICIES_PATH = ROOT_DIR / "backend" / "policies" / "default_policies.yaml"
DATABASE_PATH = DATA_DIR / "audit.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)
