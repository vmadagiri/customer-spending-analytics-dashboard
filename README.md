# Customer Spending Analytics Dashboard

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Analytics-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Quarto](https://img.shields.io/badge/Quarto-Portfolio-39729E?style=for-the-badge&logo=quarto&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-26_queries-0F766E?style=for-the-badge)

A polished retail analytics portfolio project that analyzes 50,000+ transactions to uncover revenue trends, customer behavior, product performance, discount impact, churn risk, and store-level opportunities.

## Project Links

- GitHub repository: `https://github.com/your-username/customer-spending-analytics-dashboard`
- Quarto portfolio website: `https://your-username.github.io/customer-spending-analytics-dashboard`
- Streamlit dashboard: `https://your-streamlit-app-url`

## Executive Summary

This project simulates a realistic business analytics workflow for a retail company. It generates synthetic operational data, loads it into a normalized PostgreSQL database, answers stakeholder questions with SQL, exports analysis-ready datasets with Python, and presents insights through both an interactive Streamlit dashboard and a recruiter-friendly Quarto portfolio case study.

## Business Problem

Retail leaders need to understand which customers, products, stores, seasons, and promotions drive profitable growth. This analysis converts transaction-level data into business recommendations for customer retention, merchandising, regional planning, and discount strategy.

## Tech Stack

- SQL and PostgreSQL for schema design, joins, aggregations, CTEs, views, and window functions
- Python, pandas, SQLAlchemy, and Faker for data generation, loading, automation, and exports
- Plotly and matplotlib for visualization
- Streamlit for the interactive business intelligence dashboard
- Quarto for the polished portfolio case study website
- Jupyter Notebook for exploratory analysis

## Dataset Overview

The project generates four normalized CSV files in `data/raw`:

| File | Rows | Description |
| --- | ---: | --- |
| `customers.csv` | 5,000 | Demographics, location, signup date, and loyalty tier |
| `products.csv` | 300 | Product catalog with category, subcategory, price, and cost |
| `stores.csv` | 50 | Store metadata with city, state, and region |
| `transactions.csv` | 50,000+ | Purchases with quantity, discount, payment method, revenue, and profit |

The synthetic data includes repeat customers, weighted best-selling products, holiday seasonality, and discount-driven quantity effects.

## Architecture

```mermaid
flowchart LR
    A["CSV Data<br/>customers, products, stores, transactions"] --> B["PostgreSQL<br/>normalized schema"]
    B --> C["SQL<br/>business queries and views"]
    C --> D["Python<br/>pandas + SQLAlchemy exports"]
    D --> E["Streamlit Dashboard<br/>interactive BI"]
    D --> F["Quarto Website<br/>portfolio case study"]
```

## Database Schema

```mermaid
erDiagram
    customers ||--o{ transactions : makes
    products ||--o{ transactions : includes
    stores ||--o{ transactions : records

    customers {
        int customer_id PK
        varchar first_name
        varchar last_name
        varchar email
        varchar gender
        int age
        varchar city
        char state
        date signup_date
        varchar loyalty_tier
    }

    products {
        int product_id PK
        varchar product_name
        varchar category
        varchar subcategory
        numeric unit_price
        numeric cost
    }

    stores {
        int store_id PK
        varchar store_name
        varchar city
        char state
        varchar region
    }

    transactions {
        int transaction_id PK
        int customer_id FK
        int product_id FK
        int store_id FK
        date transaction_date
        int quantity
        numeric unit_price
        numeric discount_percent
        varchar payment_method
        numeric revenue
        numeric profit
    }
```

## SQL Analysis

The project includes 26 business queries in `sql/04_business_queries.sql`, covering:

- Executive KPI summary
- Monthly revenue and profit trends
- Month-over-month growth
- Top customers and customer lifetime value
- Repeat customer rate
- RFM customer segmentation
- Churn-risk customers
- Cohort retention
- Product, category, margin, and discount analysis
- Weekday/weekend and seasonal trends
- Regional and store performance rankings
- 3-month moving averages and cumulative revenue

Techniques demonstrated include `INNER JOIN`, `LEFT JOIN`, `GROUP BY`, `HAVING`, CTEs, multiple CTEs, `ROW_NUMBER`, `RANK`, `LAG`, `SUM OVER`, moving averages, `CASE` statements, date functions, and customer segmentation.

## Streamlit Dashboard

The dashboard in `dashboard/app.py` includes:

- Executive KPI cards for revenue, profit, transactions, and average order value
- Date range, region, product category, and loyalty tier filters
- Monthly revenue and month-over-month growth charts
- Top customers, RFM segments, and churn-risk customers
- Top products, category revenue, and category margin
- Regional revenue and store rankings
- Business recommendations based on the selected data

Run it with:

```bash
streamlit run dashboard/app.py
```

## Quarto Portfolio Website

The repo also includes a Quarto website in `website/` that presents this project as a professional case study. It includes the business problem, dataset description, database schema, SQL analysis, dashboard overview, insights, recommendations, resume bullets, and screenshot gallery.

Render it with:

```bash
cd website
quarto preview
```

## How to Run Locally

```bash
cd "customer-spending-analytics-dashboard"
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a PostgreSQL database:

```bash
createdb customer_spending
```

If your PostgreSQL credentials are not `postgres/postgres`, copy `.env.example` to `.env` and edit the values:

```bash
cp .env.example .env
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
├── website/
│   ├── _quarto.yml
│   ├── index.qmd
│   ├── analysis.qmd
│   ├── dashboard.qmd
│   └── insights.qmd
├── notebooks/
│   └── customer_spending_analysis.ipynb
├── images/
└── dashboard_screenshots/
```

## Screenshots To Add

Save Streamlit screenshots in `dashboard_screenshots/` using these filenames:

- `executive_summary.png`
- `revenue_trends.png`
- `customer_analytics.png`
- `product_store_analytics.png`

These screenshots are referenced by the Quarto website.

## Key Insights

- Holiday-heavy periods create visible revenue and transaction lift.
- Discounting can increase units sold, but margin impact should be monitored by category and product.
- Repeat customers and high-RFM segments are important retention targets.
- Product category performance varies across regions, supporting localized merchandising.
- High-value customers with long purchase gaps should be prioritized for win-back campaigns.

## Resume Bullets

- Analyzed 50,000+ retail transactions by developing 20+ SQL queries using joins, CTEs, window functions, and aggregations to uncover customer behavior, revenue trends, and business insights.
- Automated a PostgreSQL analytics pipeline with Python, pandas, SQLAlchemy, and Faker to generate synthetic retail data, create normalized tables, load CSV files, and export reusable query results.
- Built an interactive Streamlit business intelligence dashboard and Quarto portfolio case study with KPI cards, Plotly visualizations, filters, business recommendations, and recruiter-ready documentation.

## Future Improvements

- Add Docker Compose for one-command PostgreSQL setup.
- Add dbt models and tests for production-style analytics engineering.
- Schedule refreshes with Airflow or GitHub Actions.
- Add churn prediction or customer propensity modeling.
- Deploy the dashboard to Streamlit Community Cloud and the Quarto site to GitHub Pages.
