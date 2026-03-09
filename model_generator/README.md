# Model Generator

Introspects the PostgreSQL database and generates a single `models.py` file with SQLAlchemy 2.0 declarative models. Also provides a **truncate-all-tables** function (no truncation by default).

## Environment

Uses these variables (from `.env` in project root or `--env`):

- `DB_NAME` (default: stakflo_dev)
- `DB_USER` (default: stakflo)
- `DB_PASSWORD` (default: stakflo@321)
- `DB_HOST` (default: 192.168.6.4)
- `DB_PORT` (default: 5432)

## Install

From project root:

```bash
pip install sqlalchemy psycopg2-binary
```

## Generate models

From project root (so that `app` and `model_generator` are both visible):

```bash
# Generate app/models.py (default)
python -m model_generator

# Custom output path
python -m model_generator --output app/models.py

# Custom .env path
python -m model_generator --env .env --output app/models.py

# Different schema
python -m model_generator --schema public --output app/models.py
```

Generated code uses `from app.db.base import Base`. The FastAPI app must provide `app.db.base` with a `Base` declarative base.

## Truncate all tables

Function: `truncate_all_tables(db_url=None, schema="public", execute=False, env_path=None)` in `model_generator.truncate`. Uses the same DB config (DB_* from .env). **By default it does not truncate** (`execute=False`): it only returns the list of table names that would be truncated.

**From code:**

```python
from model_generator import truncate_all_tables

# Dry-run: no truncation, just return list of tables
tables = truncate_all_tables(schema="public", execute=False)
print(tables)

# Actually truncate (use with care)
truncate_all_tables(schema="public", execute=True)
```

**From CLI:**

```bash
# List tables that would be truncated (no changes)
python -m model_generator --truncate

# Actually truncate all tables in public schema (CASCADE)
python -m model_generator --truncate --execute
```
