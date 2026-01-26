CREATE SCHEMA IF NOT EXISTS stg;

CREATE TABLE IF NOT EXISTS stg.events (
    batch_id TEXT,
    user_id BIGINT,
    item_id BIGINT,
    event_ts TIMESTAMP,
    event_type TEXT,
    weight NUMERIC(5,2),
    source TEXT
);

INSERT INTO stg.events (batch_id, user_id, item_id, event_ts, event_type, weight, source)
SELECT
    batch_id,
    visitor_id AS user_id,
    item_id,
    to_timestamp(event_ts_ms / 1000.0) AS event_ts,
    event_type,
    CASE event_type
        WHEN 'transaction' THEN 3
        WHEN 'addtocart' THEN 2
        ELSE 1
    END AS weight,
    'kaggle' AS source
FROM raw.events_raw
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS stg.items AS
SELECT DISTINCT item_id
FROM raw.item_properties_raw;
