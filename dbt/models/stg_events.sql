{{ config(materialized='table') }}

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
