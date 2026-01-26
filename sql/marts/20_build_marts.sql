CREATE SCHEMA IF NOT EXISTS marts;

CREATE TABLE IF NOT EXISTS marts.dim_user AS
SELECT
    user_id,
    MIN(event_ts) AS first_seen,
    MAX(event_ts) AS last_seen,
    COUNT(*) AS total_events,
    CASE
        WHEN COUNT(*) <= 2 THEN 'cold'
        WHEN COUNT(*) <= 10 THEN 'light'
        ELSE 'heavy'
    END AS segment
FROM stg.events
GROUP BY user_id;

CREATE TABLE IF NOT EXISTS marts.dim_item AS
SELECT
    item_id,
    MIN(event_ts) AS first_seen,
    MAX(event_ts) AS last_seen,
    COUNT(*) AS total_events
FROM stg.events
GROUP BY item_id;

CREATE TABLE IF NOT EXISTS marts.fact_interactions_daily AS
SELECT
    DATE(event_ts) AS ds,
    event_type,
    COUNT(*) AS events,
    COUNT(DISTINCT user_id) AS users,
    COUNT(DISTINCT item_id) AS items
FROM stg.events
GROUP BY 1,2;

CREATE TABLE IF NOT EXISTS marts.time_decay_popularity AS
SELECT
    item_id,
    SUM(weight * EXP(-0.05 * EXTRACT(EPOCH FROM (NOW() - event_ts)) / 86400.0)) AS decayed_score
FROM stg.events
GROUP BY item_id;
