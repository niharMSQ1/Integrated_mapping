"""
Introspect PostgreSQL and return Python source for SQLAlchemy 2.0 declarative models.
"""
from __future__ import annotations

import re
from typing import Any


# SQLAlchemy Declarative reserved attribute names (must use different attr name, map to DB column)
RESERVED_COLUMN_NAMES = {"metadata"}


def table_to_class_name(table_name: str) -> str:
    """Convert snake_table to PascalCase."""
    return "".join(w.capitalize() for w in table_name.split("_"))


def column_to_sqlalchemy(
    col_type: Any, col_name: str, default: Any, is_pk: bool
) -> tuple[str, str]:
    """Return (python_annotation, sa_type_str)."""
    type_str = str(col_type).upper()
    try:
        py_type_str = str(getattr(col_type, "python_type", type(col_type)))
    except Exception:
        py_type_str = ""
    # UUID
    if "UUID" in type_str or "UUID" in py_type_str:
        if is_pk:
            return "uuid.UUID", "UUID(as_uuid=True), primary_key=True, default=uuid.uuid4"
        return "uuid.UUID | None", "UUID(as_uuid=True), nullable=True"
    # String types
    if "TEXT" in type_str:
        return "str | None", "Text, nullable=True"
    if "VARCHAR" in type_str or "CHAR" in type_str:
        size = 255
        if "VARCHAR" in type_str:
            m = re.search(r"VARCHAR\((\d+)\)", type_str)
            if m:
                size = int(m.group(1))
        return "str | None", f"String({size}), nullable=True"
    # Int
    if "INT" in type_str and "BIGINT" not in type_str or "SERIAL" in type_str:
        return "int | None", "Integer, nullable=True"
    if "BIGINT" in type_str:
        return "int | None", "BigInteger, nullable=True"
    # Bool
    if "BOOL" in type_str:
        return "bool", "Boolean, default=False"
    # Date/time
    if "TIMESTAMP" in type_str:
        return "datetime | None", "DateTime(timezone=True), nullable=True"
    if "DATE" in type_str and "TIME" not in type_str:
        return "date | None", "Date, nullable=True"
    # JSON
    if "JSON" in type_str or "JSONB" in type_str:
        return "dict | Any | None", "JSONB, nullable=True"
    # Numeric
    if "NUMERIC" in type_str or "DECIMAL" in type_str:
        return "float | None", "Numeric, nullable=True"
    return "Any", "String(255), nullable=True"


def generate_models_python(inspector: Any, schema: str = "public") -> str:
    """Generate full models.py source from SQLAlchemy inspector."""
    lines = [
        '"""SQLAlchemy 2.0 models generated from database introspection. Do not edit by hand."""',
        "from __future__ import annotations",
        "",
        "import uuid",
        "from datetime import date, datetime",
        "from typing import Any",
        "",
        "from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text",
        "from sqlalchemy.dialects.postgresql import JSONB, UUID",
        "from sqlalchemy.orm import Mapped, mapped_column, relationship",
        "from sqlalchemy.sql import func",
        "",
        "from app.db.base import Base",
        "",
    ]
    table_names = inspector.get_table_names(schema=schema)
    for table_name in sorted(table_names):
        class_name = table_to_class_name(table_name)
        columns = inspector.get_columns(table_name, schema=schema)
        pk_cols = inspector.get_pk_constraint(table_name, schema=schema).get("constrained_columns") or []
        # SQLAlchemy requires a PK: if DB table has none, use first column as PK (e.g. cache.key)
        if not pk_cols and columns:
            pk_cols = [columns[0]["name"]]
        fks = inspector.get_foreign_keys(table_name, schema=schema)
        lines.append(f"class {class_name}(Base):")
        lines.append(f'    __tablename__ = "{table_name}"')
        lines.append("")
        for col in columns:
            name = col["name"]
            col_type = col["type"]
            nullable = col.get("nullable", True)
            default = col.get("default")
            is_pk = name in pk_cols
            py_ann, sa_part = column_to_sqlalchemy(col_type, name, default, is_pk)
            if is_pk:
                if "primary_key=True" not in sa_part:
                    sa_part = sa_part.replace(", nullable=True", "").replace(", nullable=False", "").rstrip() + ", primary_key=True"
                elif "nullable=True" in sa_part:
                    sa_part = sa_part.replace(", nullable=True", "")
            elif not nullable:
                sa_part = sa_part.replace("nullable=True", "nullable=False")
            attr_name = name + "_" if name in RESERVED_COLUMN_NAMES else name
            if name in RESERVED_COLUMN_NAMES:
                lines.append(f'    {attr_name}: Mapped[{py_ann}] = mapped_column("{name}", {sa_part})')
            else:
                lines.append(f"    {attr_name}: Mapped[{py_ann}] = mapped_column({sa_part})")
        lines.append("")
    return "\n".join(lines)


def run_introspection(db_url: str, schema: str = "public") -> str:
    """Connect to DB, introspect, return generated source."""
    from sqlalchemy import create_engine
    from sqlalchemy import inspect
    engine = create_engine(db_url)
    inspector = inspect(engine)
    return generate_models_python(inspector, schema=schema)
