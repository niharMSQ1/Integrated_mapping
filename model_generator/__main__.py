"""
CLI entrypoint. Run from project root:

  python -m model_generator --output app/models.py
  python -m model_generator --output app/models.py --env .env
  python -m model_generator --truncate              # list tables (no truncation)
  python -m model_generator --truncate --execute     # actually truncate all tables
"""
import argparse
import sys
from pathlib import Path

from model_generator.config import get_db_url, load_env
from model_generator.introspect import run_introspection
from model_generator.truncate import truncate_all_tables


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Introspect PostgreSQL and generate SQLAlchemy 2.0 models.py"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output file path (e.g. app/models.py). Default: app/models.py in project root.",
    )
    parser.add_argument(
        "--env",
        type=Path,
        default=None,
        help="Path to .env file. Default: .env in project root.",
    )
    parser.add_argument(
        "--schema",
        type=str,
        default="public",
        help="PostgreSQL schema to introspect. Default: public.",
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Run truncate_all_tables(): list tables (no truncation unless --execute).",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="With --truncate: actually truncate all tables (CASCADE). Ignored without --truncate.",
    )
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parent.parent
    env_path = args.env or project_root / ".env"
    env = load_env(env_path)

    if args.truncate:
        try:
            tables = truncate_all_tables(
                db_url=None,
                schema=args.schema,
                execute=args.execute,
                env_path=str(env_path),
            )
            if args.execute:
                print(f"Truncated {len(tables)} table(s): {', '.join(tables)}")
            else:
                print(f"Would truncate {len(tables)} table(s) (dry-run): {', '.join(tables)}")
                print("Run with --execute to actually truncate.")
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    output_path = args.output or project_root / "app" / "models.py"
    db_url = get_db_url(env)
    try:
        source = run_introspection(db_url, schema=args.schema)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(source, encoding="utf-8")
        print(f"Written: {output_path}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
