"""Run SQL business questions and export results for dashboarding."""

from __future__ import annotations

from dataclasses import dataclass
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy.engine import Engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from config import DATA_PROCESSED_DIR, IMAGES_DIR, SQL_DIR, get_engine
from src.utils import export_dataframe


QUERY_PATTERN = re.compile(
    r"-- Query (?P<number>\d+): (?P<title>.+?)\n"
    r"-- Business question: (?P<question>.+?)\n"
    r"(?P<sql>.*?);(?=\s*-- Query|\s*\Z)",
    re.DOTALL,
)


@dataclass(frozen=True)
class BusinessQuery:
    """Structured representation of one titled SQL business question."""

    number: str
    title: str
    question: str
    sql: str

    @property
    def output_name(self) -> str:
        """Return a stable export name that preserves query order."""
        return f"{self.number}_{self.title}"


def parse_business_queries(sql_text: str) -> list[BusinessQuery]:
    """Parse titled SQL queries from sql/04_business_queries.sql."""
    queries: list[BusinessQuery] = []
    for match in QUERY_PATTERN.finditer(sql_text):
        queries.append(
            BusinessQuery(
                number=match.group("number"),
                title=match.group("title").strip(),
                question=match.group("question").strip(),
                sql=match.group("sql").strip(),
            )
        )
    if not queries:
        raise ValueError("No business queries were parsed. Check sql/04_business_queries.sql formatting.")
    return queries


def run_and_export_queries(engine: Engine | None = None) -> list[Path]:
    """Run all business queries and export each result to data/processed."""
    engine = engine or get_engine()
    sql_text = (SQL_DIR / "04_business_queries.sql").read_text(encoding="utf-8")
    queries = parse_business_queries(sql_text)
    exported_paths: list[Path] = []
    manifest_rows: list[dict[str, str | int]] = []

    with engine.connect() as connection:
        for query in queries:
            df = pd.read_sql_query(query.sql, connection)
            path = export_dataframe(df, query.output_name)
            exported_paths.append(path)
            manifest_rows.append(
                {
                    "query_number": query.number,
                    "title": query.title,
                    "business_question": query.question,
                    "rows_exported": len(df),
                    "output_file": path.name,
                }
            )
            print(f"Exported {query.title} -> {path.name} ({len(df):,} rows)")

    pd.DataFrame(manifest_rows).to_csv(DATA_PROCESSED_DIR / "query_manifest.csv", index=False)

    create_visualizations()
    return exported_paths


def create_visualizations() -> None:
    """Create simple PNG charts from processed query outputs."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    monthly_path = DATA_PROCESSED_DIR / "02_monthly_revenue_trend.csv"
    category_path = DATA_PROCESSED_DIR / "06_revenue_by_product_category.csv"
    region_path = DATA_PROCESSED_DIR / "07_revenue_by_store_region.csv"

    if monthly_path.exists():
        monthly = pd.read_csv(monthly_path, parse_dates=["month"])
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(monthly["month"], monthly["revenue"], marker="o", color="#2563eb")
        ax.set_title("Monthly Revenue Trend")
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue")
        ax.grid(True, alpha=0.3)
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(IMAGES_DIR / "monthly_revenue_trend.png", dpi=160)
        plt.close(fig)

    if category_path.exists():
        category = pd.read_csv(category_path).sort_values("revenue")
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.barh(category["category"], category["revenue"], color="#0f766e")
        ax.set_title("Revenue by Product Category")
        ax.set_xlabel("Revenue")
        fig.tight_layout()
        fig.savefig(IMAGES_DIR / "revenue_by_category.png", dpi=160)
        plt.close(fig)

    if region_path.exists():
        region = pd.read_csv(region_path).sort_values("revenue")
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(region["region"], region["revenue"], color="#9333ea")
        ax.set_title("Revenue by Store Region")
        ax.set_xlabel("Region")
        ax.set_ylabel("Revenue")
        fig.tight_layout()
        fig.savefig(IMAGES_DIR / "revenue_by_region.png", dpi=160)
        plt.close(fig)


def main() -> None:
    """CLI entry point."""
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    exported = run_and_export_queries()
    print(f"Finished exporting {len(exported)} query result files.")


if __name__ == "__main__":
    main()
