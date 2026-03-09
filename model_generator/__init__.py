"""
Model generator: introspect PostgreSQL database and generate SQLAlchemy 2.0 models.py.

Uses DB_* from .env (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT).
Run: python -m model_generator --output app/models.py

Also provides truncate_all_tables() to optionally truncate all tables (dry-run by default).
"""
from model_generator.truncate import truncate_all_tables

__all__ = ["truncate_all_tables"]
