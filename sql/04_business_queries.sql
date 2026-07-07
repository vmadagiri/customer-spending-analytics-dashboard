-- Customer Spending Analytics Dashboard
-- Business SQL analysis for PostgreSQL.
-- Each query is intentionally written as a recruiter-readable business question.

-- Query 01: Executive KPI Summary
-- Business question: What are total revenue, total profit, total transactions, units sold, and average order value?
SELECT
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    COUNT(*) AS total_transactions,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(revenue) / NULLIF(COUNT(*), 0), 2) AS average_order_value,
    ROUND(100 * SUM(profit) / NULLIF(SUM(revenue), 0), 2) AS profit_margin_percent
FROM transactions;

-- Query 02: Monthly Revenue Trend
-- Business question: How are revenue, profit, and transaction volume trending by month?
SELECT
    DATE_TRUNC('month', transaction_date)::date AS month,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    COUNT(*) AS transactions,
    SUM(quantity) AS units_sold
FROM transactions
GROUP BY DATE_TRUNC('month', transaction_date)::date
ORDER BY month;

-- Query 03: Month-over-Month Revenue Growth
-- Business question: Which months grew or declined compared with the prior month?
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', transaction_date)::date AS month,
        SUM(revenue) AS revenue
    FROM transactions
    GROUP BY DATE_TRUNC('month', transaction_date)::date
),
growth AS (
    SELECT
        month,
        revenue,
        LAG(revenue) OVER (ORDER BY month) AS previous_month_revenue
    FROM monthly_revenue
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(previous_month_revenue, 2) AS previous_month_revenue,
    ROUND(100 * (revenue - previous_month_revenue) / NULLIF(previous_month_revenue, 0), 2) AS mom_growth_percent
FROM growth
ORDER BY month;

-- Query 04: Top 10 Customers by Revenue
-- Business question: Which customers are highest value by total spend?
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.loyalty_tier,
    COUNT(t.transaction_id) AS transactions,
    ROUND(SUM(t.revenue), 2) AS revenue,
    ROUND(AVG(t.revenue), 2) AS average_order_value
FROM customers c
INNER JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id, customer_name, c.loyalty_tier
ORDER BY revenue DESC
LIMIT 10;

-- Query 05: Top 10 Products by Revenue
-- Business question: Which products generate the most sales dollars?
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(t.quantity) AS units_sold,
    COUNT(t.transaction_id) AS transactions,
    ROUND(SUM(t.revenue), 2) AS revenue
FROM products p
INNER JOIN transactions t ON p.product_id = t.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY revenue DESC
LIMIT 10;

-- Query 06: Revenue by Product Category
-- Business question: Which product categories contribute the most revenue and profit?
SELECT
    p.category,
    COUNT(DISTINCT p.product_id) AS products,
    SUM(t.quantity) AS units_sold,
    ROUND(SUM(t.revenue), 2) AS revenue,
    ROUND(SUM(t.profit), 2) AS profit,
    ROUND(100 * SUM(t.profit) / NULLIF(SUM(t.revenue), 0), 2) AS profit_margin_percent
FROM transactions t
INNER JOIN products p ON t.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;

-- Query 07: Revenue by Store Region
-- Business question: Which geographic regions drive the most revenue and profit?
SELECT
    s.region,
    COUNT(DISTINCT s.store_id) AS stores,
    COUNT(t.transaction_id) AS transactions,
    ROUND(SUM(t.revenue), 2) AS revenue,
    ROUND(SUM(t.profit), 2) AS profit,
    ROUND(SUM(t.revenue) / NULLIF(COUNT(DISTINCT s.store_id), 0), 2) AS revenue_per_store
FROM stores s
INNER JOIN transactions t ON s.store_id = t.store_id
GROUP BY s.region
ORDER BY revenue DESC;

-- Query 08: Average Order Value by Month
-- Business question: Is average order value improving over time?
SELECT
    DATE_TRUNC('month', transaction_date)::date AS month,
    ROUND(AVG(revenue), 2) AS average_order_value,
    ROUND(SUM(revenue), 2) AS revenue,
    COUNT(*) AS transactions
FROM transactions
GROUP BY DATE_TRUNC('month', transaction_date)::date
ORDER BY month;

-- Query 09: Repeat Customer Rate
-- Business question: What share of purchasing customers bought more than once?
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(*) AS transactions
    FROM transactions
    GROUP BY customer_id
)
SELECT
    COUNT(*) AS purchasing_customers,
    COUNT(*) FILTER (WHERE transactions > 1) AS repeat_customers,
    ROUND(100.0 * COUNT(*) FILTER (WHERE transactions > 1) / NULLIF(COUNT(*), 0), 2) AS repeat_customer_rate
FROM customer_orders;

-- Query 10: Customer Lifetime Value
-- Business question: What is lifetime value by customer?
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.loyalty_tier,
    MIN(t.transaction_date) AS first_purchase_date,
    MAX(t.transaction_date) AS last_purchase_date,
    COUNT(t.transaction_id) AS total_orders,
    ROUND(SUM(t.revenue), 2) AS lifetime_value,
    ROUND(SUM(t.profit), 2) AS lifetime_profit
FROM customers c
INNER JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id, customer_name, c.loyalty_tier
ORDER BY lifetime_value DESC;

-- Query 11: RFM Segmentation
-- Business question: How are customers distributed across RFM segments?
SELECT
    rfm_segment,
    COUNT(*) AS customers,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(frequency), 1) AS avg_frequency,
    ROUND(AVG(monetary_value), 2) AS avg_monetary_value
FROM vw_customer_rfm
GROUP BY rfm_segment
ORDER BY customers DESC;

-- Query 12: Churn-risk Customers
-- Business question: Which previously active customers have not purchased recently?
SELECT
    customer_id,
    first_name || ' ' || last_name AS customer_name,
    loyalty_tier,
    recency_days,
    frequency,
    ROUND(monetary_value, 2) AS monetary_value
FROM vw_customer_rfm
WHERE recency_days >= 180
  AND frequency >= 5
ORDER BY monetary_value DESC
LIMIT 100;

-- Query 13: Cohort Retention by Signup Month
-- Business question: How many customers in each signup cohort returned in later purchase months?
WITH first_purchase AS (
    SELECT
        customer_id,
        MIN(DATE_TRUNC('month', transaction_date)::date) AS first_purchase_month
    FROM transactions
    GROUP BY customer_id
),
activity AS (
    SELECT DISTINCT
        customer_id,
        DATE_TRUNC('month', transaction_date)::date AS activity_month
    FROM transactions
),
cohorts AS (
    SELECT
        DATE_TRUNC('month', c.signup_date)::date AS signup_month,
        fp.customer_id,
        fp.first_purchase_month,
        a.activity_month,
        (
            (DATE_PART('year', a.activity_month) - DATE_PART('year', fp.first_purchase_month)) * 12
            + DATE_PART('month', a.activity_month) - DATE_PART('month', fp.first_purchase_month)
        )::int AS months_since_first_purchase
    FROM customers c
    INNER JOIN first_purchase fp ON c.customer_id = fp.customer_id
    INNER JOIN activity a ON fp.customer_id = a.customer_id
)
SELECT
    signup_month,
    months_since_first_purchase,
    COUNT(DISTINCT customer_id) AS active_customers
FROM cohorts
WHERE months_since_first_purchase BETWEEN 0 AND 12
GROUP BY signup_month, months_since_first_purchase
ORDER BY signup_month, months_since_first_purchase;

-- Query 14: Best-selling Products by Quantity
-- Business question: Which products move the highest number of units?
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(t.quantity) AS units_sold,
    ROUND(SUM(t.revenue), 2) AS revenue,
    ROUND(SUM(t.profit), 2) AS profit
FROM products p
INNER JOIN transactions t ON p.product_id = t.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY units_sold DESC
LIMIT 20;

-- Query 15: Highest-margin Products
-- Business question: Which products have strong margin after reaching meaningful sales volume?
SELECT
    p.product_id,
    p.product_name,
    p.category,
    ROUND(SUM(t.revenue), 2) AS revenue,
    ROUND(SUM(t.profit), 2) AS profit,
    ROUND(100 * SUM(t.profit) / NULLIF(SUM(t.revenue), 0), 2) AS profit_margin_percent
FROM products p
INNER JOIN transactions t ON p.product_id = t.product_id
GROUP BY p.product_id, p.product_name, p.category
HAVING SUM(t.revenue) >= 1000
ORDER BY profit_margin_percent DESC, revenue DESC
LIMIT 20;

-- Query 16: Discount Impact on Revenue
-- Business question: How do discount bands affect order volume, revenue, and profit?
SELECT
    CASE
        WHEN discount_percent = 0 THEN 'No discount'
        WHEN discount_percent <= 0.10 THEN 'Low discount'
        WHEN discount_percent <= 0.20 THEN 'Medium discount'
        ELSE 'High discount'
    END AS discount_band,
    COUNT(*) AS transactions,
    SUM(quantity) AS units_sold,
    ROUND(AVG(revenue), 2) AS avg_order_revenue,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(100 * SUM(profit) / NULLIF(SUM(revenue), 0), 2) AS profit_margin_percent
FROM transactions
GROUP BY discount_band
ORDER BY revenue DESC;

-- Query 17: Revenue by Payment Method
-- Business question: Which payment methods are most common and valuable?
SELECT
    payment_method,
    COUNT(*) AS transactions,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(AVG(revenue), 2) AS average_order_value,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS transaction_share_percent
FROM transactions
GROUP BY payment_method
ORDER BY revenue DESC;

-- Query 18: Weekday vs Weekend Sales
-- Business question: Are customers spending more on weekdays or weekends?
SELECT
    CASE
        WHEN EXTRACT(ISODOW FROM transaction_date) IN (6, 7) THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    COUNT(*) AS transactions,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(AVG(revenue), 2) AS average_order_value
FROM transactions
GROUP BY day_type
ORDER BY revenue DESC;

-- Query 19: Seasonal Sales Trends
-- Business question: Which seasons have the strongest sales performance?
SELECT
    CASE
        WHEN EXTRACT(MONTH FROM transaction_date) IN (12, 1, 2) THEN 'Winter'
        WHEN EXTRACT(MONTH FROM transaction_date) IN (3, 4, 5) THEN 'Spring'
        WHEN EXTRACT(MONTH FROM transaction_date) IN (6, 7, 8) THEN 'Summer'
        ELSE 'Fall'
    END AS season,
    COUNT(*) AS transactions,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(AVG(revenue), 2) AS average_order_value
FROM transactions
GROUP BY season
ORDER BY revenue DESC;

-- Query 20: Customer Loyalty Tier Performance
-- Business question: How do loyalty tiers compare on revenue, frequency, and order value?
SELECT
    c.loyalty_tier,
    COUNT(DISTINCT c.customer_id) AS customers,
    COUNT(t.transaction_id) AS transactions,
    ROUND(COALESCE(SUM(t.revenue), 0), 2) AS revenue,
    ROUND(AVG(t.revenue), 2) AS average_order_value,
    ROUND(COALESCE(SUM(t.revenue), 0) / NULLIF(COUNT(DISTINCT c.customer_id), 0), 2) AS revenue_per_customer
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.loyalty_tier
ORDER BY revenue DESC;

-- Query 21: Customers with Declining Spend
-- Business question: Which customers spent less in their latest active month than the prior active month?
WITH monthly_customer_spend AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', transaction_date)::date AS month,
        SUM(revenue) AS monthly_revenue
    FROM transactions
    GROUP BY customer_id, DATE_TRUNC('month', transaction_date)::date
),
spend_with_lag AS (
    SELECT
        customer_id,
        month,
        monthly_revenue,
        LAG(monthly_revenue) OVER (PARTITION BY customer_id ORDER BY month) AS previous_month_revenue,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY month DESC) AS recency_rank
    FROM monthly_customer_spend
)
SELECT
    customer_id,
    month AS latest_active_month,
    ROUND(monthly_revenue, 2) AS latest_month_revenue,
    ROUND(previous_month_revenue, 2) AS previous_month_revenue,
    ROUND(100 * (monthly_revenue - previous_month_revenue) / NULLIF(previous_month_revenue, 0), 2) AS change_percent
FROM spend_with_lag
WHERE recency_rank = 1
  AND previous_month_revenue IS NOT NULL
  AND monthly_revenue < previous_month_revenue
ORDER BY change_percent ASC
LIMIT 100;

-- Query 22: Top Category per Region
-- Business question: Which product category leads revenue in each region?
WITH category_region_revenue AS (
    SELECT
        s.region,
        p.category,
        SUM(t.revenue) AS revenue
    FROM transactions t
    INNER JOIN products p ON t.product_id = p.product_id
    INNER JOIN stores s ON t.store_id = s.store_id
    GROUP BY s.region, p.category
),
ranked AS (
    SELECT
        region,
        category,
        revenue,
        RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS category_rank
    FROM category_region_revenue
)
SELECT
    region,
    category,
    ROUND(revenue, 2) AS revenue
FROM ranked
WHERE category_rank = 1
ORDER BY region;

-- Query 23: Product Ranking Within Each Category
-- Business question: Which products rank highest within each category by revenue?
WITH product_revenue AS (
    SELECT
        p.category,
        p.product_id,
        p.product_name,
        SUM(t.revenue) AS revenue
    FROM products p
    INNER JOIN transactions t ON p.product_id = t.product_id
    GROUP BY p.category, p.product_id, p.product_name
)
SELECT
    category,
    product_id,
    product_name,
    ROUND(revenue, 2) AS revenue,
    RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS revenue_rank
FROM product_revenue
ORDER BY category, revenue_rank;

-- Query 24: 3-Month Moving Average Revenue
-- Business question: What is the smoothed revenue trend after short-term volatility?
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', transaction_date)::date AS month,
        SUM(revenue) AS revenue
    FROM transactions
    GROUP BY DATE_TRUNC('month', transaction_date)::date
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS three_month_moving_avg
FROM monthly
ORDER BY month;

-- Query 25: Store Performance Ranking
-- Business question: Which stores are strongest by revenue within their region?
SELECT
    s.region,
    s.store_id,
    s.store_name,
    COUNT(t.transaction_id) AS transactions,
    ROUND(SUM(t.revenue), 2) AS revenue,
    ROUND(SUM(t.profit), 2) AS profit,
    ROW_NUMBER() OVER (PARTITION BY s.region ORDER BY SUM(t.revenue) DESC) AS region_store_rank
FROM stores s
INNER JOIN transactions t ON s.store_id = t.store_id
GROUP BY s.region, s.store_id, s.store_name
ORDER BY s.region, region_store_rank;

-- Query 26: Running Revenue by Month
-- Business question: How much cumulative revenue has the business generated over time?
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', transaction_date)::date AS month,
        SUM(revenue) AS revenue
    FROM transactions
    GROUP BY DATE_TRUNC('month', transaction_date)::date
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(SUM(revenue) OVER (ORDER BY month), 2) AS cumulative_revenue
FROM monthly
ORDER BY month;
