"""Create PostgreSQL tables and load generated CSV files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from config import DATA_RAW_DIR, get_engine
from src.utils import execute_sql_file


LOAD_ORDER = [
    ("customers", "customers.csv"),
    ("products", "products.csv"),
    ("stores", "stores.csv"),
    ("transactions", "transactions.csv"),
]


def load_csvs(engine) -> None:
    """Load raw CSV files into PostgreSQL tables."""
    for table_name, filename in LOAD_ORDER:
        path = DATA_RAW_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}. Run src/generate_data.py first.")
        df = pd.read_csv(path)
        df.to_sql(table_name, engine, if_exists="append", index=False, method="multi", chunksize=5_000)
        print(f"Loaded {len(df):,} rows into {table_name}")


def rebuild_database(skip_cleaning: bool = False) -> None:
    """Recreate tables, load CSVs, run cleaning checks, and create views."""
    engine = get_engine()
    print("Creating tables...")
    execute_sql_file(engine, "01_create_tables.sql")
    print("Loading CSV files...")
    load_csvs(engine)
    if not skip_cleaning:
        print("Running cleaning and validation SQL...")
        execute_sql_file(engine, "03_data_cleaning.sql")
    print("Creating views...")
    execute_sql_file(engine, "05_views.sql")
    print("Database is ready.")


def parse_args() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description="Load synthetic retail CSVs into PostgreSQL.")
    parser.add_argument("--skip-cleaning", action="store_true", help="Skip data cleaning SQL after loading.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rebuild_database(skip_cleaning=args.skip_cleaning)
