"""
Create all tables from app.models in the database.

Uses DB_* from .env (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT).
To use database "stakflo_dev_nihar": set DB_NAME=stakflo_dev_nihar in .env,
or run: python -m scripts.migrate --db-name stakflo_dev_nihar

Run from project root:
  python -m scripts.migrate
  python -m scripts.migrate --db-name stakflo_dev_nihar
"""
import argparse
import sys
from pathlib import Path

# Ensure project root is on path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


def get_db_url(db_name: str | None, env_path: Path | None) -> str:
    """Build sync PostgreSQL URL. If db_name is set, override DB_NAME."""
    from model_generator.config import get_db_url as _get_db_url, load_env
    env = load_env(env_path)
    if db_name:
        env = {**env, "DB_NAME": db_name}
    return _get_db_url(env)


def run_migrate(db_name: str | None = None, env_path: Path | None = None) -> list[str]:
    """Create all tables in the database. Uses app.models (registers with Base.metadata)."""
    from sqlalchemy import create_engine
    from app.db.base import Base
    import app.models  # noqa: F401 - register all models with Base.metadata

    url = get_db_url(db_name, env_path)
    engine = create_engine(url)
    Base.metadata.create_all(bind=engine)
    return sorted(Base.metadata.tables.keys())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create all tables from app.models in the database (DB_* from .env)."
    )
    parser.add_argument(
        "--db-name",
        type=str,
        default=None,
        help="Override database name (e.g. stakflo_dev_nihar). Default: use DB_NAME from .env.",
    )
    parser.add_argument(
        "--env",
        type=Path,
        default=None,
        help="Path to .env file. Default: .env in project root.",
    )
    args = parser.parse_args()
    env_path = args.env or _project_root / ".env"
    try:
        tables = run_migrate(db_name=args.db_name, env_path=env_path)
        print(f"Created {len(tables)} table(s) in database: {', '.join(tables)}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
