"""
Truncate all tables in a schema. Uses same DB config as introspection (DB_* from .env).

By default does not truncate: call with execute=True to actually run TRUNCATE.
"""
from __future__ import annotations

from typing import List


def truncate_all_tables(
    db_url: str | None = None,
    schema: str = "public",
    execute: bool = False,
    env_path: str | None = None,
) -> List[str]:
    """
    Get list of tables in the schema and optionally truncate them (CASCADE).

    Args:
        db_url: PostgreSQL URL. If None, built from .env via config.get_db_url().
        schema: Schema name. Default "public".
        execute: If False (default), no truncation is performed; only the list of
                 table names that would be truncated is returned.
                 If True, runs TRUNCATE ... CASCADE on all tables in the schema.

    Returns:
        List of table names (in the order they would be / were truncated).
        When execute=False, this is the list that would be truncated.
    """
    from pathlib import Path

    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import Engine

    if db_url is None:
        from model_generator.config import get_db_url, load_env
        root = Path(__file__).resolve().parent.parent
        env = load_env(Path(env_path) if env_path else root / ".env")
        db_url = get_db_url(env)

    engine: Engine = create_engine(db_url)
    from sqlalchemy import inspect
    inspector = inspect(engine)
    table_names = inspector.get_table_names(schema=schema)

    if not table_names:
        return []

    if not execute:
        return sorted(table_names)

    # Disable triggers and truncate all tables in one go with CASCADE
    quoted_schema = f'"{schema}"'
    quoted_tables = ", ".join(f'{quoted_schema}."{t}"' for t in sorted(table_names))
    sql = f"TRUNCATE TABLE {quoted_tables} RESTART IDENTITY CASCADE"
    with engine.begin() as conn:
        conn.execute(text(sql))
    return sorted(table_names)
