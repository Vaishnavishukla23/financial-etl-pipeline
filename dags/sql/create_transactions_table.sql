CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR PRIMARY KEY,
    user_id VARCHAR,
    transaction_date TIMESTAMP,
    amount NUMERIC,
    category VARCHAR
);
