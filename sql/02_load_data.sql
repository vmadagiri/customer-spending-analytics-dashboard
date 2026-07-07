-- This file documents the expected CSV loading order.
-- The Python loader uses pandas + SQLAlchemy so paths work cross-platform.
-- Loading order:
-- 1. customers
-- 2. products
-- 3. stores
-- 4. transactions

SELECT 'Use src/load_to_postgres.py to load CSV files from data/raw into PostgreSQL.' AS instruction;
