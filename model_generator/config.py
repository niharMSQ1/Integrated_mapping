"""Load DB config from .env for introspection (sync connection)."""
import os
from pathlib import Path
from urllib.parse import quote_plus


def load_env(env_path: Path | None = None) -> dict[str, str]:
    """Load .env file into a dict. If env_path is None, search parent dirs for .env."""
    if env_path and env_path.exists():
        path = env_path
    else:
        # Default: .env in project root (parent of model_generator)
        root = Path(__file__).resolve().parent.parent
        path = root / ".env"
    out: dict[str, str] = {}
    if not path.exists():
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def get_db_url(env: dict[str, str] | None = None) -> str:
    """Build sync PostgreSQL URL from env dict or os.environ."""
    env = env or load_env()
    user = env.get("DB_USER", os.getenv("DB_USER", "stakflo"))
    password = env.get("DB_PASSWORD", os.getenv("DB_PASSWORD", "stakflo@321"))
    host = env.get("DB_HOST", os.getenv("DB_HOST", "192.168.6.4"))
    port = env.get("DB_PORT", os.getenv("DB_PORT", "5432"))
    name = env.get("DB_NAME", os.getenv("DB_NAME", "stakflo_dev"))
    # Quote user/password so special chars (e.g. @ in password) don't break the URL
    user_quoted = quote_plus(user)
    password_quoted = quote_plus(password)
    return f"postgresql://{user_quoted}:{password_quoted}@{host}:{port}/{name}"
