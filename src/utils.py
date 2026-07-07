"""Shared utilities for file paths, SQL execution, and output handling."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from config import DATA_PROCESSED_DIR, SQL_DIR


def ensure_directories() -> None:
    """Create expected project output directories."""
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def read_sql_file(filename: str) -> str:
    """Read a SQL file from the project sql directory."""
    return (SQL_DIR / filename).read_text(encoding="utf-8")


def split_sql_statements(sql: str) -> list[str]:
    """Split a SQL script into executable statements.

    The project SQL files avoid semicolons inside string literals, so this
    lightweight splitter keeps the dependency footprint small while still
    making multi-statement files portable across SQLAlchemy/PostgreSQL setups.
    """
    return [statement.strip() for statement in sql.split(";") if statement.strip()]


def execute_sql_file(engine: Engine, filename: str) -> None:
    """Execute all SQL statements in a SQL file."""
    sql = read_sql_file(filename)
    with engine.begin() as connection:
        for statement in split_sql_statements(sql):
            connection.execute(text(statement))


def slugify(value: str) -> str:
    """Convert a title into a stable filename-friendly slug."""
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def export_dataframe(df: pd.DataFrame, name: str, output_dir: Path = DATA_PROCESSED_DIR) -> Path:
    """Export a dataframe to data/processed using a slugified filename."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{slugify(name)}.csv"
    df.to_csv(path, index=False)
    return path
