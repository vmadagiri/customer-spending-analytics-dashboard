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


PAGE_TITLE = "Customer Spending Analytics Dashboard"
COLOR_SEQUENCE = ["#1f5eff", "#0f766e", "#b7791f", "#7c3aed", "#dc2626", "#334155"]

st.set_page_config(page_title=PAGE_TITLE, layout="wide", initial_sidebar_state="expanded")


def apply_theme() -> None:
    """Apply dashboard-level CSS for a polished portfolio presentation."""
    st.markdown(
        """
        <style>
        .stApp {
            background: #f6f8fb;
            color: #172033;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }

        [data-testid="stSidebar"] {
            background: #f8fafc;
            border-right: 1px solid #e2e8f0;
        }

        h1, h2, h3 {
            letter-spacing: 0;
            color: #0f172a !important;
        }

        .hero-panel {
            padding: 1.6rem 1.75rem;
            border: 1px solid #dbe4ef;
            border-radius: 0.85rem;
            background: linear-gradient(135deg, #ffffff 0%, #eef5ff 100%);
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07);
            margin-bottom: 1.4rem;
        }

        .hero-panel h1 {
            color: #0f172a !important;
            margin-top: 0;
        }

        .hero-panel p {
            color: #526173;
            max-width: 900px;
            margin-bottom: 0;
            line-height: 1.55;
        }

        .kpi-card {
            padding: 1.05rem 1.15rem;
            border: 1px solid #dbe4ef;
            border-radius: 0.8rem;
            background: #ffffff;
            box-shadow: 0 14px 35px rgba(15, 23, 42, 0.06);
            min-height: 120px;
        }

        .kpi-label {
            color: #64748b;
            font-size: 0.84rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            margin-bottom: 0.45rem;
        }

        .kpi-value {
            color: #0f172a;
            font-size: 2rem;
            font-weight: 850;
            line-height: 1.15;
        }

        .kpi-caption {
            color: #64748b;
            font-size: 0.86rem;
            margin-top: 0.35rem;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid #e2e8f0;
            border-radius: 0.75rem;
            overflow: hidden;
        }

        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li {
            color: #334155;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


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


def kpi_card(label: str, value: str, caption: str) -> None:
    """Render a custom KPI card."""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_chart(fig, height: int = 420):
    """Apply consistent dashboard chart styling."""
    fig.update_layout(
        height=height,
        template="plotly_white",
        colorway=COLOR_SEQUENCE,
        margin=dict(l=20, r=20, t=60, b=20),
        title_font=dict(size=18, color="#172033"),
        font=dict(color="#334155"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#e2e8f0")
    return fig


def build_customer_metrics(filtered: pd.DataFrame) -> pd.DataFrame:
    """Aggregate transaction data into customer-level metrics."""
    customer_metrics = (
        filtered.groupby(["customer_id", "first_name", "last_name", "loyalty_tier"], as_index=False)
        .agg(
            transactions=("transaction_id", "count"),
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            last_purchase=("transaction_date", "max"),
        )
    )
    customer_metrics["customer_name"] = customer_metrics["first_name"] + " " + customer_metrics["last_name"]
    customer_metrics["recency_days"] = (filtered["transaction_date"].max() - customer_metrics["last_purchase"]).dt.days
    customer_metrics["rfm_segment"] = pd.cut(
        customer_metrics["recency_days"],
        bins=[-1, 30, 90, 180, 10_000],
        labels=["Champions", "Loyal Customers", "Needs Attention", "At Risk"],
    )
    return customer_metrics


def dataframe_currency(df: pd.DataFrame, currency_columns: list[str]) -> pd.DataFrame:
    """Return a display copy with selected numeric columns formatted as currency."""
    display = df.copy()
    for column in currency_columns:
        if column in display:
            display[column] = display[column].map(lambda value: f"${value:,.2f}")
    return display


apply_theme()
df = load_data()

st.markdown(
    """
    <div class="hero-panel">
        <h1>Customer Spending Analytics Dashboard</h1>
        <p>
        Executive retail analytics across revenue, customer retention, product performance,
        discount behavior, and store rankings. Use the filters to inspect business performance
        across regions, loyalty tiers, categories, and time periods.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("Dashboard Filters")
    st.caption("Refine the analysis by time period, region, category, and loyalty tier.")
    min_date = df["transaction_date"].min().date()
    max_date = df["transaction_date"].max().date()
    date_range = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    all_regions = sorted(df["region"].dropna().unique())
    all_categories = sorted(df["category"].dropna().unique())
    all_tiers = sorted(df["loyalty_tier"].dropna().unique())

    regions = st.multiselect("Region", all_regions, default=all_regions)
    categories = st.multiselect("Product category", all_categories, default=all_categories)
    tiers = st.multiselect("Loyalty tier", all_tiers, default=all_tiers)

    st.divider()
    st.caption("Dataset: 50,000 transactions, 5,000 customers, 300 products, 50 stores.")

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

total_revenue = filtered["revenue"].sum()
total_profit = filtered["profit"].sum()
total_transactions = filtered["transaction_id"].nunique()
average_order_value = total_revenue / total_transactions
profit_margin = 100 * total_profit / total_revenue

st.subheader("Executive Summary")
kpi_cols = st.columns(4)
with kpi_cols[0]:
    kpi_card("Total revenue", format_currency(total_revenue), "Gross sales after discounts")
with kpi_cols[1]:
    kpi_card("Total profit", format_currency(total_profit), f"{profit_margin:.1f}% margin")
with kpi_cols[2]:
    kpi_card("Transactions", f"{total_transactions:,}", "Filtered purchase records")
with kpi_cols[3]:
    kpi_card("Average order value", format_currency(average_order_value), "Revenue per transaction")

st.subheader("Revenue Trends")
monthly = (
    filtered.assign(month=filtered["transaction_date"].dt.to_period("M").dt.to_timestamp())
    .groupby("month", as_index=False)
    .agg(revenue=("revenue", "sum"), profit=("profit", "sum"), transactions=("transaction_id", "count"))
)
monthly["mom_growth_percent"] = monthly["revenue"].pct_change() * 100

trend_cols = st.columns(2)
trend_cols[0].plotly_chart(
    style_chart(px.line(monthly, x="month", y="revenue", markers=True, title="Monthly Revenue"), 410),
    width="stretch",
)
trend_cols[1].plotly_chart(
    style_chart(px.bar(monthly, x="month", y="mom_growth_percent", title="Month-over-Month Growth (%)"), 410),
    width="stretch",
)

st.subheader("Customer Analytics")
customer_metrics = build_customer_metrics(filtered)
segment_counts = customer_metrics["rfm_segment"].value_counts().reset_index()
segment_counts.columns = ["segment", "customers"]

customer_cols = st.columns([1.2, 1])
top_customers = customer_metrics.sort_values("revenue", ascending=False)[
    ["customer_id", "customer_name", "loyalty_tier", "transactions", "revenue", "profit"]
].head(10)
customer_cols[0].dataframe(
    dataframe_currency(top_customers, ["revenue", "profit"]),
    width="stretch",
    hide_index=True,
)
customer_cols[1].plotly_chart(
    style_chart(px.bar(segment_counts, x="segment", y="customers", title="RFM Segment Distribution"), 390),
    width="stretch",
)

st.markdown("#### Churn-Risk Customers")
churn_risk = (
    customer_metrics[(customer_metrics["recency_days"] >= 180) & (customer_metrics["transactions"] >= 5)]
    .sort_values("revenue", ascending=False)[["customer_id", "customer_name", "loyalty_tier", "recency_days", "transactions", "revenue"]]
    .head(20)
)
st.dataframe(dataframe_currency(churn_risk, ["revenue"]), width="stretch", hide_index=True)

st.subheader("Product Analytics")
product_metrics = (
    filtered.groupby(["product_id", "product_name", "category"], as_index=False)
    .agg(units_sold=("quantity", "sum"), revenue=("revenue", "sum"), profit=("profit", "sum"))
)
category_metrics = (
    filtered.groupby("category", as_index=False)
    .agg(revenue=("revenue", "sum"), profit=("profit", "sum"), units_sold=("quantity", "sum"))
)
category_metrics["profit_margin_percent"] = 100 * category_metrics["profit"] / category_metrics["revenue"]

product_cols = st.columns([1.1, 1, 1])
product_cols[0].dataframe(
    dataframe_currency(product_metrics.sort_values("revenue", ascending=False).head(10), ["revenue", "profit"]),
    width="stretch",
    hide_index=True,
)
product_cols[1].plotly_chart(
    style_chart(px.bar(category_metrics.sort_values("revenue", ascending=False), x="category", y="revenue", title="Revenue by Category"), 390),
    width="stretch",
)
product_cols[2].plotly_chart(
    style_chart(px.bar(category_metrics.sort_values("profit_margin_percent", ascending=False), x="category", y="profit_margin_percent", title="Profit Margin by Category"), 390),
    width="stretch",
)

st.subheader("Store Analytics")
region_metrics = filtered.groupby("region", as_index=False).agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
store_ranking = (
    filtered.groupby(["region", "store_id", "store_name"], as_index=False)
    .agg(transactions=("transaction_id", "count"), revenue=("revenue", "sum"), profit=("profit", "sum"))
    .sort_values(["region", "revenue"], ascending=[True, False])
)
store_ranking["region_rank"] = store_ranking.groupby("region")["revenue"].rank(method="first", ascending=False).astype(int)

store_cols = st.columns([1, 1.2])
store_cols[0].plotly_chart(
    style_chart(px.bar(region_metrics.sort_values("revenue", ascending=False), x="region", y="revenue", title="Revenue by Region"), 390),
    width="stretch",
)
store_cols[1].dataframe(
    dataframe_currency(store_ranking.sort_values(["region", "region_rank"]).head(20), ["revenue", "profit"]),
    width="stretch",
    hide_index=True,
)

st.subheader("Business Recommendations")
top_category = category_metrics.sort_values("revenue", ascending=False).iloc[0]["category"]
top_region = region_metrics.sort_values("revenue", ascending=False).iloc[0]["region"]
at_risk_count = int((customer_metrics["rfm_segment"] == "At Risk").sum())
margin_leader = category_metrics.sort_values("profit_margin_percent", ascending=False).iloc[0]["category"]

rec_cols = st.columns(2)
rec_cols[0].success(f"Prioritize inventory depth and promotional visibility for {top_category}, the highest-revenue category in the filtered period.")
rec_cols[0].info(f"Use {top_region} as a benchmark region and compare staffing, store mix, and campaign timing against lower-performing regions.")
rec_cols[1].warning(f"Launch win-back campaigns for {at_risk_count:,} at-risk customers with high historical spend and long purchase gaps.")
rec_cols[1].success(f"Protect margin in {margin_leader} by using targeted discounts instead of broad markdowns.")
