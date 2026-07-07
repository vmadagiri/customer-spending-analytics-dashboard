"""Shared utilities for file paths, SQL execution, and output handling."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from config import DATA_PROCESSED_DIR, SQL_DIR


def ensure_directories() -> None:
    """Create expected project output directories."""
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def read_sql_file(filename: str) -> str:
    """Read a SQL file from the project sql directory."""
    return (SQL_DIR / filename).read_text(encoding="utf-8")


def execute_sql_file(engine, filename: str) -> None:
    """Execute all SQL statements in a SQL file."""
    sql = read_sql_file(filename)
    with engine.begin() as connection:
        for statement in sql.split(";"):
            statement = statement.strip()
            if statement:
                connection.execute(text(statement))


def slugify(value: str) -> str:
    """Convert a title into a stable filename-friendly slug."""
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def export_dataframe(df: pd.DataFrame, name: str) -> Path:
    """Export a dataframe to data/processed using a slugified filename."""
    ensure_directories()
    path = DATA_PROCESSED_DIR / f"{slugify(name)}.csv"
    df.to_csv(path, index=False)
    return path
