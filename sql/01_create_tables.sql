DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS stores CASCADE;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    gender VARCHAR(30) NOT NULL,
    age INTEGER NOT NULL CHECK (age BETWEEN 18 AND 100),
    city VARCHAR(120) NOT NULL,
    state CHAR(2) NOT NULL,
    signup_date DATE NOT NULL,
    loyalty_tier VARCHAR(20) NOT NULL CHECK (loyalty_tier IN ('Bronze', 'Silver', 'Gold', 'Platinum'))
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL CHECK (category IN ('Electronics', 'Clothing', 'Beauty', 'Home', 'Grocery', 'Sports', 'Books')),
    subcategory VARCHAR(100) NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price > 0),
    cost NUMERIC(10, 2) NOT NULL CHECK (cost > 0),
    CHECK (cost < unit_price)
);

CREATE TABLE stores (
    store_id INTEGER PRIMARY KEY,
    store_name VARCHAR(255) NOT NULL,
    city VARCHAR(120) NOT NULL,
    state CHAR(2) NOT NULL,
    region VARCHAR(30) NOT NULL CHECK (region IN ('Northeast', 'South', 'Midwest', 'West'))
);

CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    store_id INTEGER NOT NULL REFERENCES stores(store_id),
    transaction_date DATE NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price > 0),
    discount_percent NUMERIC(5, 2) NOT NULL CHECK (discount_percent >= 0 AND discount_percent <= 1),
    payment_method VARCHAR(30) NOT NULL CHECK (payment_method IN ('Credit Card', 'Debit Card', 'PayPal', 'Cash', 'Gift Card')),
    revenue NUMERIC(12, 2) NOT NULL CHECK (revenue >= 0),
    profit NUMERIC(12, 2) NOT NULL
);

CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_customer_id ON transactions(customer_id);
CREATE INDEX idx_transactions_product_id ON transactions(product_id);
CREATE INDEX idx_transactions_store_id ON transactions(store_id);
