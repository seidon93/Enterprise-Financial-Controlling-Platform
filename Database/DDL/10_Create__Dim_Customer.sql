CREATE TABLE IF NOT EXISTS warehouse.dim_customer (
    customer_key INTEGER PRIMARY KEY,
    customer_code VARCHAR(20) NOT NULL UNIQUE,
    customer_name VARCHAR(200) NOT NULL,
    customer_type VARCHAR(50),
    country_code VARCHAR(5),
    city VARCHAR(100),
    industry VARCHAR(100),
    payment_terms INTEGER,
    credit_limit NUMERIC(18, 2),
    risk_category VARCHAR(20),
    active_from DATE,
    active_to DATE,
    is_active BOOLEAN NOT NULL
);