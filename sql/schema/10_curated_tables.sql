CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.dim_user (
    user_id BIGINT PRIMARY KEY,
    first_seen_ts TIMESTAMP,
    first_seen_date DATE,
    country_proxy TEXT,
    device_proxy TEXT,
    acquisition_channel_proxy TEXT
);

CREATE TABLE IF NOT EXISTS analytics.dim_product (
    product_id BIGINT PRIMARY KEY,
    category_id BIGINT,
    parent_category_id BIGINT,
    price_proxy NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS analytics.dim_date (
    date_key INT PRIMARY KEY,
    date DATE UNIQUE,
    year SMALLINT,
    month SMALLINT,
    week SMALLINT,
    day_of_week SMALLINT
);

CREATE TABLE IF NOT EXISTS analytics.dim_campaign (
    campaign_id TEXT PRIMARY KEY,
    channel TEXT,
    campaign_name TEXT,
    start_date DATE,
    end_date DATE
);

CREATE TABLE IF NOT EXISTS analytics.fact_events (
    event_id BIGSERIAL PRIMARY KEY,
    event_ts TIMESTAMP,
    event_date DATE,
    user_id BIGINT,
    product_id BIGINT,
    event_type TEXT,
    transaction_id BIGINT,
    session_id TEXT
);

CREATE TABLE IF NOT EXISTS analytics.fact_orders (
    order_id BIGINT,
    order_ts TIMESTAMP,
    order_date DATE,
    order_date_key INT,
    user_id BIGINT,
    product_id BIGINT,
    quantity INT,
    unit_price NUMERIC(10, 2),
    discount NUMERIC(5, 2),
    revenue NUMERIC(12, 2),
    category_id BIGINT
);

CREATE TABLE IF NOT EXISTS analytics.fact_marketing_spend (
    date_key INT,
    campaign_id TEXT,
    channel TEXT,
    impressions INT,
    clicks INT,
    spend NUMERIC(12, 2)
);

CREATE INDEX IF NOT EXISTS idx_fact_events_user_date
    ON analytics.fact_events (user_id, event_date);

CREATE INDEX IF NOT EXISTS idx_fact_orders_user_date
    ON analytics.fact_orders (user_id, order_date);

CREATE INDEX IF NOT EXISTS idx_fact_marketing_date_channel
    ON analytics.fact_marketing_spend (date_key, channel);
