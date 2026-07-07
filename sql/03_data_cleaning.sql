-- Data cleaning and quality checks.
-- These statements are intentionally conservative because the generator already
-- produces clean data. They can be run after loading to validate assumptions.

DELETE FROM transactions
WHERE quantity <= 0
   OR unit_price <= 0
   OR discount_percent < 0
   OR discount_percent > 1;

DELETE FROM products
WHERE unit_price <= 0
   OR cost <= 0
   OR cost >= unit_price;

-- Standardize text columns in case source CSVs are edited manually.
UPDATE customers
SET email = LOWER(TRIM(email)),
    first_name = INITCAP(TRIM(first_name)),
    last_name = INITCAP(TRIM(last_name));

UPDATE stores
SET region = INITCAP(TRIM(region));

-- Validate core row counts after cleaning.
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'stores', COUNT(*) FROM stores
UNION ALL
SELECT 'transactions', COUNT(*) FROM transactions;
