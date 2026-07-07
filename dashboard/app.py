"""Streamlit dashboard for the Customer Spending Analytics project."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from config import DATA_RAW_DIR  # noqa: E402


st.set_page_config(page_title="Customer Spending Analytics Dashboard", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load raw CSVs and return transaction-level analytics data."""
    required = ["customers.csv", "products.csv", "stores.csv", "transactions.csv"]
    missing = [name for name in required if not (DATA_RAW_DIR / name).exists()]
    if missing:
        st.error("Missing raw CSV files. Run `python src/generate_data.py` first.")
        st.stop()

    customers = pd.read_csv(DATA_RAW_DIR / "customers.csv", parse_dates=["signup_date"])
    products = pd.read_csv(DATA_RAW_DIR / "products.csv")
    stores = pd.read_csv(DATA_RAW_DIR / "stores.csv")
    transactions = pd.read_csv(DATA_RAW_DIR / "transactions.csv", parse_dates=["transaction_date"])

    df = (
        transactions.merge(customers, on="customer_id", how="left")
        .merge(products[["product_id", "product_name", "category", "subcategory", "cost"]], on="product_id", how="left")
        .merge(stores[["store_id", "store_name", "region"]], on="store_id", how="left")
    )
    if "revenue" not in df.columns:
        df["revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount_percent"])
    if "profit" not in df.columns:
        df["profit"] = df["revenue"] - df["quantity"] * df["cost"]
    return df


def format_currency(value: float) -> str:
    """Format a number as compact US currency."""
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


df = load_data()

st.title("Customer Spending Analytics Dashboard")

with st.sidebar:
    st.header("Filters")
    min_date = df["transaction_date"].min().date()
    max_date = df["transaction_date"].max().date()
    date_range = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    regions = st.multiselect("Region", sorted(df["region"].dropna().unique()), default=sorted(df["region"].dropna().unique()))
    categories = st.multiselect("Product category", sorted(df["category"].dropna().unique()), default=sorted(df["category"].dropna().unique()))
    tiers = st.multiselect("Loyalty tier", sorted(df["loyalty_tier"].dropna().unique()), default=sorted(df["loyalty_tier"].dropna().unique()))

if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start_date, end_date = pd.to_datetime(min_date), pd.to_datetime(max_date)

filtered = df[
    (df["transaction_date"].between(start_date, end_date))
    & (df["region"].isin(regions))
    & (df["category"].isin(categories))
    & (df["loyalty_tier"].isin(tiers))
].copy()

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

st.subheader("Executive Summary")
total_revenue = filtered["revenue"].sum()
total_profit = filtered["profit"].sum()
total_transactions = filtered["transaction_id"].nunique()
average_order_value = total_revenue / total_transactions

kpi_cols = st.columns(4)
kpi_cols[0].metric("Total revenue", format_currency(total_revenue))
kpi_cols[1].metric("Total profit", format_currency(total_profit))
kpi_cols[2].metric("Total transactions", f"{total_transactions:,}")
kpi_cols[3].metric("Average order value", format_currency(average_order_value))

st.subheader("Revenue Trends")
monthly = (
    filtered.assign(month=filtered["transaction_date"].dt.to_period("M").dt.to_timestamp())
    .groupby("month", as_index=False)
    .agg(revenue=("revenue", "sum"), profit=("profit", "sum"), transactions=("transaction_id", "count"))
)
monthly["mom_growth_percent"] = monthly["revenue"].pct_change() * 100

trend_cols = st.columns(2)
trend_cols[0].plotly_chart(
    px.line(monthly, x="month", y="revenue", markers=True, title="Monthly Revenue"),
    use_container_width=True,
)
trend_cols[1].plotly_chart(
    px.bar(monthly, x="month", y="mom_growth_percent", title="Month-over-Month Growth (%)"),
    use_container_width=True,
)

st.subheader("Customer Analytics")
customer_metrics = (
    filtered.groupby(["customer_id", "first_name", "last_name", "loyalty_tier"], as_index=False)
    .agg(transactions=("transaction_id", "count"), revenue=("revenue", "sum"), last_purchase=("transaction_date", "max"))
)
customer_metrics["customer_name"] = customer_metrics["first_name"] + " " + customer_metrics["last_name"]
customer_metrics["recency_days"] = (filtered["transaction_date"].max() - customer_metrics["last_purchase"]).dt.days
customer_metrics["rfm_segment"] = pd.cut(
    customer_metrics["recency_days"],
    bins=[-1, 30, 90, 180, 10_000],
    labels=["Champions", "Loyal Customers", "Needs Attention", "At Risk"],
)

customer_cols = st.columns(2)
customer_cols[0].dataframe(
    customer_metrics.sort_values("revenue", ascending=False)[["customer_id", "customer_name", "loyalty_tier", "transactions", "revenue"]].head(10),
    use_container_width=True,
    hide_index=True,
)
segment_counts = customer_metrics["rfm_segment"].value_counts().reset_index()
segment_counts.columns = ["segment", "customers"]
customer_cols[1].plotly_chart(px.bar(segment_counts, x="segment", y="customers", title="RFM Segment Distribution"), use_container_width=True)
st.dataframe(
    customer_metrics[(customer_metrics["recency_days"] >= 180) & (customer_metrics["transactions"] >= 5)]
    .sort_values("revenue", ascending=False)[["customer_id", "customer_name", "loyalty_tier", "recency_days", "transactions", "revenue"]]
    .head(20),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Product Analytics")
product_metrics = (
    filtered.groupby(["product_id", "product_name", "category"], as_index=False)
    .agg(units_sold=("quantity", "sum"), revenue=("revenue", "sum"), profit=("profit", "sum"))
)
category_metrics = (
    filtered.groupby("category", as_index=False)
    .agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
)
category_metrics["profit_margin_percent"] = 100 * category_metrics["profit"] / category_metrics["revenue"]

product_cols = st.columns(3)
product_cols[0].dataframe(product_metrics.sort_values("revenue", ascending=False).head(10), use_container_width=True, hide_index=True)
product_cols[1].plotly_chart(px.bar(category_metrics.sort_values("revenue", ascending=False), x="category", y="revenue", title="Revenue by Category"), use_container_width=True)
product_cols[2].plotly_chart(px.bar(category_metrics.sort_values("profit_margin_percent", ascending=False), x="category", y="profit_margin_percent", title="Profit Margin by Category"), use_container_width=True)

st.subheader("Store Analytics")
region_metrics = filtered.groupby("region", as_index=False).agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
store_ranking = (
    filtered.groupby(["region", "store_id", "store_name"], as_index=False)
    .agg(transactions=("transaction_id", "count"), revenue=("revenue", "sum"), profit=("profit", "sum"))
    .sort_values(["region", "revenue"], ascending=[True, False])
)
store_ranking["region_rank"] = store_ranking.groupby("region")["revenue"].rank(method="first", ascending=False).astype(int)

store_cols = st.columns(2)
store_cols[0].plotly_chart(px.bar(region_metrics.sort_values("revenue", ascending=False), x="region", y="revenue", title="Revenue by Region"), use_container_width=True)
store_cols[1].dataframe(store_ranking.sort_values(["region", "region_rank"]).head(20), use_container_width=True, hide_index=True)

st.subheader("Business Recommendations")
top_category = category_metrics.sort_values("revenue", ascending=False).iloc[0]["category"]
top_region = region_metrics.sort_values("revenue", ascending=False).iloc[0]["region"]
at_risk_count = int((customer_metrics["rfm_segment"] == "At Risk").sum())
margin_leader = category_metrics.sort_values("profit_margin_percent", ascending=False).iloc[0]["category"]

st.markdown(
    f"""
1. Prioritize inventory depth and promotional visibility for **{top_category}**, the highest-revenue category in the filtered period.
2. Use **{top_region}** as a benchmark region and compare staffing, store mix, and campaign timing against lower-performing regions.
3. Launch win-back campaigns for **{at_risk_count:,} at-risk customers** with high historical spend and long purchase gaps.
4. Protect margin in **{margin_leader}** by using targeted discounts instead of broad markdowns.
5. Expand loyalty-tier personalization because higher-frequency customers create measurable revenue concentration.
"""
)
