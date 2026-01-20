\echo 'Building curated tables in analytics schema'

TRUNCATE analytics.fact_marketing_spend;
TRUNCATE analytics.fact_orders;
TRUNCATE analytics.fact_events RESTART IDENTITY;
TRUNCATE analytics.dim_campaign;
TRUNCATE analytics.dim_product;
TRUNCATE analytics.dim_user;
TRUNCATE analytics.dim_date;

-- dim_date
WITH bounds AS (
    SELECT
        to_timestamp(MIN(event_ts_ms) / 1000.0)::date AS min_date,
        to_timestamp(MAX(event_ts_ms) / 1000.0)::date AS max_date
    FROM raw.events
),
series AS (
    SELECT generate_series(min_date, max_date, interval '1 day')::date AS d
    FROM bounds
)
INSERT INTO analytics.dim_date (date_key, date, year, month, week, day_of_week)
SELECT
    to_char(d, 'YYYYMMDD')::int AS date_key,
    d AS date,
    EXTRACT(YEAR FROM d)::smallint AS year,
    EXTRACT(MONTH FROM d)::smallint AS month,
    EXTRACT(WEEK FROM d)::smallint AS week,
    EXTRACT(DOW FROM d)::smallint AS day_of_week
FROM series;

-- dim_user
INSERT INTO analytics.dim_user (
    user_id,
    first_seen_ts,
    first_seen_date,
    country_proxy,
    device_proxy,
    acquisition_channel_proxy
)
SELECT
    visitor_id AS user_id,
    to_timestamp(MIN(event_ts_ms) / 1000.0) AS first_seen_ts,
    to_timestamp(MIN(event_ts_ms) / 1000.0)::date AS first_seen_date,
    CASE MOD(visitor_id, 5)
        WHEN 0 THEN 'US'
        WHEN 1 THEN 'UK'
        WHEN 2 THEN 'DE'
        WHEN 3 THEN 'IN'
        ELSE 'BR'
    END AS country_proxy,
    CASE MOD(visitor_id, 3)
        WHEN 0 THEN 'Mobile'
        WHEN 1 THEN 'Desktop'
        ELSE 'Tablet'
    END AS device_proxy,
    CASE MOD(visitor_id, 4)
        WHEN 0 THEN 'organic'
        WHEN 1 THEN 'paid_search'
        WHEN 2 THEN 'social'
        ELSE 'email'
    END AS acquisition_channel_proxy
FROM raw.events
GROUP BY visitor_id;

-- dim_product
WITH category_props AS (
    SELECT
        item_id,
        CASE WHEN value ~ '^[0-9]+$' THEN value::bigint END AS category_id,
        property_ts_ms
    FROM raw.item_properties
    WHERE property = 'categoryid'
),
latest_category AS (
    SELECT DISTINCT ON (item_id)
        item_id,
        category_id
    FROM category_props
    WHERE category_id IS NOT NULL
    ORDER BY item_id, property_ts_ms DESC
)
INSERT INTO analytics.dim_product (product_id, category_id, parent_category_id, price_proxy)
SELECT
    lc.item_id AS product_id,
    lc.category_id,
    ct.parent_id AS parent_category_id,
    ROUND((MOD(lc.item_id, 10000)::numeric / 100.0) + 5.0, 2) AS price_proxy
FROM latest_category lc
LEFT JOIN raw.category_tree ct
    ON lc.category_id = ct.category_id;

-- dim_campaign (proxy)
WITH dates AS (
    SELECT MIN(date) AS min_date, MAX(date) AS max_date
    FROM analytics.dim_date
)
INSERT INTO analytics.dim_campaign (campaign_id, channel, campaign_name, start_date, end_date)
SELECT 'organic', 'organic', 'Organic', min_date, max_date FROM dates
UNION ALL
SELECT 'paid_search', 'paid_search', 'Paid Search', min_date, max_date FROM dates
UNION ALL
SELECT 'social', 'social', 'Social', min_date, max_date FROM dates
UNION ALL
SELECT 'email', 'email', 'Email', min_date, max_date FROM dates;

-- fact_events with sessionization (30-minute inactivity split)
WITH ordered AS (
    SELECT
        visitor_id,
        item_id,
        event_type,
        transaction_id,
        to_timestamp(event_ts_ms / 1000.0) AS event_ts,
        LAG(to_timestamp(event_ts_ms / 1000.0)) OVER (
            PARTITION BY visitor_id
            ORDER BY event_ts_ms
        ) AS prev_ts
    FROM raw.events
),
sessionized AS (
    SELECT
        *,
        SUM(
            CASE
                WHEN prev_ts IS NULL OR event_ts - prev_ts > interval '30 minutes' THEN 1
                ELSE 0
            END
        ) OVER (PARTITION BY visitor_id ORDER BY event_ts) AS session_seq
    FROM ordered
)
INSERT INTO analytics.fact_events (
    event_ts,
    event_date,
    user_id,
    product_id,
    event_type,
    transaction_id,
    session_id
)
SELECT
    event_ts,
    event_ts::date AS event_date,
    visitor_id AS user_id,
    item_id AS product_id,
    event_type,
    transaction_id,
    visitor_id::text || '-' || session_seq::text AS session_id
FROM sessionized;

-- fact_orders (transaction events only)
INSERT INTO analytics.fact_orders (
    order_id,
    order_ts,
    order_date,
    order_date_key,
    user_id,
    product_id,
    quantity,
    unit_price,
    discount,
    revenue,
    category_id
)
SELECT
    fe.transaction_id AS order_id,
    fe.event_ts AS order_ts,
    fe.event_ts::date AS order_date,
    to_char(fe.event_ts, 'YYYYMMDD')::int AS order_date_key,
    fe.user_id,
    fe.product_id,
    1 AS quantity,
    COALESCE(dp.price_proxy, 0.0) AS unit_price,
    0.0 AS discount,
    COALESCE(dp.price_proxy, 0.0) AS revenue,
    dp.category_id
FROM analytics.fact_events fe
LEFT JOIN analytics.dim_product dp
    ON fe.product_id = dp.product_id
WHERE fe.event_type = 'transaction'
  AND fe.transaction_id IS NOT NULL;

-- fact_marketing_spend (proxy spend)
WITH daily AS (
    SELECT
        fe.event_date,
        du.acquisition_channel_proxy AS channel,
        COUNT(*) FILTER (WHERE fe.event_type = 'view') AS impressions,
        COUNT(*) FILTER (WHERE fe.event_type = 'addtocart') AS clicks
    FROM analytics.fact_events fe
    JOIN analytics.dim_user du
        ON fe.user_id = du.user_id
    GROUP BY fe.event_date, du.acquisition_channel_proxy
),
costed AS (
    SELECT
        event_date,
        channel,
        impressions,
        clicks,
        (impressions * 0.005 + clicks * 0.50) AS spend
    FROM daily
)
INSERT INTO analytics.fact_marketing_spend (
    date_key,
    campaign_id,
    channel,
    impressions,
    clicks,
    spend
)
SELECT
    to_char(event_date, 'YYYYMMDD')::int AS date_key,
    channel AS campaign_id,
    channel,
    impressions,
    clicks,
    ROUND(spend::numeric, 2) AS spend
FROM costed;

\echo 'Curated build complete'
