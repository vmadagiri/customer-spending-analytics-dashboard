# Customer Spending Analytics Dashboard

A GitHub-ready retail analytics case study that analyzes 50,000+ synthetic transactions to uncover revenue trends, customer behavior, product performance, discount impact, churn risk, and store-level opportunities.

## Business Problem

Retail leaders need a reliable way to understand which customers, products, stores, and seasons drive profitable growth. This project simulates a real analytics workflow: generate operational data, load it into PostgreSQL, answer business questions with SQL, export analysis-ready results, and present the findings in an interactive Streamlit dashboard.

## Tools Used

- PostgreSQL and SQL
- Python, pandas, SQLAlchemy, Faker
- Plotly and matplotlib
- Streamlit
- Jupyter Notebook

## Dataset Overview

The project generates four normalized CSV files in `data/raw`:

- `customers.csv`: 5,000 customers with demographics, signup dates, and loyalty tiers.
- `products.csv`: 300 products across Electronics, Clothing, Beauty, Home, Grocery, Sports, and Books.
- `stores.csv`: 50 stores across Northeast, South, Midwest, and West regions.
- `transactions.csv`: 50,000+ transactions with repeat purchases, weighted best sellers, discounts, seasonal demand, revenue, and profit.

## Database Schema

The PostgreSQL schema includes normalized `customers`, `products`, `stores`, and `transactions` tables with primary keys, foreign keys, `NOT NULL` constraints, `CHECK` constraints, and indexes on transaction date plus customer, product, and store IDs.

## SQL Techniques Demonstrated

The SQL analysis includes 26 business queries using:

- `INNER JOIN` and `LEFT JOIN`
- `GROUP BY`, `HAVING`, and aggregations
- Single and multiple CTEs
- Window functions including `ROW_NUMBER`, `RANK`, `LAG`, and `SUM OVER`
- 3-month moving averages
- `CASE` statements
- Date functions and cohort logic
- Customer segmentation through RFM analysis

## Dashboard Features

The Streamlit dashboard includes:

- Executive KPIs: total revenue, total profit, transactions, and average order value
- Revenue trends: monthly revenue and month-over-month growth
- Customer analytics: top customers, RFM segments, and churn-risk customers
- Product analytics: top products, category revenue, and category margin
- Store analytics: regional revenue and store rankings
- Filters for date range, region, product category, and loyalty tier
- Business recommendations generated from the filtered view

## Key Insights to Look For

- Holiday periods should show stronger transaction volume and revenue.
- Discount bands can increase units sold while compressing profit margin.
- A small group of repeat customers should contribute a meaningful share of revenue.
- Product category performance varies by region, which supports localized merchandising.
- Churn-risk customers can be prioritized by high historical value and long purchase gaps.

## How to Run Locally

```bash
cd "/Users/vaishnavimadagiri/Documents/New project/customer-spending-analytics-dashboard"
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a PostgreSQL database:

```bash
createdb customer_spending
```

If your PostgreSQL credentials are not `postgres/postgres`, create a `.env` file:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=customer_spending
DB_USER=postgres
DB_PASSWORD=postgres
```

Generate data, load PostgreSQL, export query results, and run the dashboard:

```bash
python src/generate_data.py --transactions 50000
python -m src.load_to_postgres
python -m src.run_queries
streamlit run dashboard/app.py
```

You can also run the dashboard immediately after generating CSVs:

```bash
python src/generate_data.py --transactions 50000
streamlit run dashboard/app.py
```

## Folder Structure

```text
customer-spending-analytics-dashboard/
├── README.md
├── requirements.txt
├── .gitignore
├── config.py
├── data/
│   ├── raw/
│   └── processed/
├── sql/
│   ├── 01_create_tables.sql
│   ├── 02_load_data.sql
│   ├── 03_data_cleaning.sql
│   ├── 04_business_queries.sql
│   └── 05_views.sql
├── src/
│   ├── generate_data.py
│   ├── load_to_postgres.py
│   ├── run_queries.py
│   └── utils.py
├── dashboard/
│   └── app.py
├── notebooks/
│   └── customer_spending_analysis.ipynb
├── images/
└── dashboard_screenshots/
```

## Screenshots

Add screenshots after running Streamlit:

- Executive Summary with filters visible
- Revenue Trends section
- Customer Analytics section with RFM chart
- Product Analytics section
- Store Analytics and Business Recommendations

## Resume Bullets

- Analyzed 50,000+ retail transactions by developing 20+ SQL queries using joins, CTEs, window functions, and aggregations to uncover customer behavior, revenue trends, and business insights.
- Automated a PostgreSQL analytics pipeline with Python, pandas, SQLAlchemy, and Faker to generate synthetic retail data, create normalized tables, load CSV files, and export reusable query results.
- Built an interactive Streamlit business intelligence dashboard with Plotly visualizations, KPI cards, and filters for date range, region, product category, and loyalty tier.

## Future Improvements

- Add dbt models and tests for production-style analytics engineering.
- Schedule refreshes with Airflow or GitHub Actions.
- Add customer propensity modeling for churn and next-best-offer recommendations.
- Deploy the dashboard to Streamlit Community Cloud.
- Add Docker Compose for one-command PostgreSQL setup.
