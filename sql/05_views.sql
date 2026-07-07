DROP VIEW IF EXISTS vw_transaction_details;
DROP VIEW IF EXISTS vw_monthly_revenue;
DROP VIEW IF EXISTS vw_customer_rfm;

CREATE VIEW vw_transaction_details AS
SELECT
    t.transaction_id,
    t.transaction_date,
    t.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    c.gender,
    c.age,
    c.city AS customer_city,
    c.state AS customer_state,
    c.signup_date,
    c.loyalty_tier,
    t.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    t.store_id,
    s.store_name,
    s.city AS store_city,
    s.state AS store_state,
    s.region,
    t.quantity,
    t.unit_price,
    t.discount_percent,
    t.payment_method,
    t.revenue,
    t.profit
FROM transactions t
INNER JOIN customers c ON t.customer_id = c.customer_id
INNER JOIN products p ON t.product_id = p.product_id
INNER JOIN stores s ON t.store_id = s.store_id;

CREATE VIEW vw_monthly_revenue AS
SELECT
    DATE_TRUNC('month', transaction_date)::date AS month,
    SUM(revenue) AS revenue,
    SUM(profit) AS profit,
    COUNT(*) AS transactions,
    SUM(quantity) AS units_sold
FROM transactions
GROUP BY 1;

CREATE VIEW vw_customer_rfm AS
WITH customer_metrics AS (
    SELECT
        c.customer_id,
        c.first_name,
        c.last_name,
        c.loyalty_tier,
        MAX(t.transaction_date) AS last_purchase_date,
        COUNT(t.transaction_id) AS frequency,
        COALESCE(SUM(t.revenue), 0) AS monetary_value,
        DATE_PART('day', (SELECT MAX(transaction_date) FROM transactions) - MAX(t.transaction_date)) AS recency_days
    FROM customers c
    LEFT JOIN transactions t ON c.customer_id = t.customer_id
    GROUP BY c.customer_id, c.first_name, c.last_name, c.loyalty_tier
),
scores AS (
    SELECT
        *,
        NTILE(5) OVER (ORDER BY recency_days DESC NULLS FIRST) AS recency_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS frequency_score,
        NTILE(5) OVER (ORDER BY monetary_value ASC) AS monetary_score
    FROM customer_metrics
)
SELECT
    *,
    CASE
        WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4 THEN 'Champions'
        WHEN recency_score >= 3 AND frequency_score >= 3 THEN 'Loyal Customers'
        WHEN recency_score <= 2 AND frequency_score >= 3 THEN 'At Risk'
        WHEN recency_score >= 4 AND frequency_score <= 2 THEN 'New or Promising'
        ELSE 'Needs Attention'
    END AS rfm_segment
FROM scores;
