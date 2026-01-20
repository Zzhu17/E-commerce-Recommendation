CREATE OR REPLACE VIEW analytics.vw_funnel_30d AS
WITH bounds AS (
    SELECT MAX(event_date) AS max_date
    FROM analytics.fact_events
),
base AS (
    SELECT
        fe.user_id,
        MAX(CASE WHEN fe.event_type = 'view' THEN 1 ELSE 0 END) AS has_view,
        MAX(CASE WHEN fe.event_type = 'addtocart' THEN 1 ELSE 0 END) AS has_add_to_cart,
        MAX(CASE WHEN fe.event_type = 'transaction' THEN 1 ELSE 0 END) AS has_purchase
    FROM analytics.fact_events fe
    CROSS JOIN bounds b
    WHERE fe.event_date BETWEEN b.max_date - interval '30 days' AND b.max_date
    GROUP BY fe.user_id
),
counts AS (
    SELECT
        COUNT(*) AS users,
        SUM(has_view) AS view_users,
        SUM(has_add_to_cart) AS add_to_cart_users,
        SUM(has_purchase) AS purchase_users
    FROM base
)
SELECT
    users,
    view_users,
    add_to_cart_users,
    purchase_users,
    ROUND(add_to_cart_users::numeric / NULLIF(view_users, 0), 4) AS view_to_cart_cvr,
    ROUND(purchase_users::numeric / NULLIF(add_to_cart_users, 0), 4) AS cart_to_purchase_cvr,
    ROUND(purchase_users::numeric / NULLIF(view_users, 0), 4) AS view_to_purchase_cvr
FROM counts;

CREATE OR REPLACE VIEW analytics.vw_segment_channel_30d AS
WITH bounds AS (
    SELECT MAX(order_date) AS max_date
    FROM analytics.fact_orders
),
orders AS (
    SELECT
        fo.user_id,
        COUNT(DISTINCT fo.order_id) AS orders,
        SUM(fo.revenue) AS revenue
    FROM analytics.fact_orders fo
    CROSS JOIN bounds b
    WHERE fo.order_date BETWEEN b.max_date - interval '30 days' AND b.max_date
    GROUP BY fo.user_id
),
joined AS (
    SELECT
        du.acquisition_channel_proxy AS channel,
        du.user_id,
        COALESCE(o.orders, 0) AS orders,
        COALESCE(o.revenue, 0.0) AS revenue,
        CASE WHEN COALESCE(o.orders, 0) > 0 THEN 1 ELSE 0 END AS converted
    FROM analytics.dim_user du
    LEFT JOIN orders o
        ON du.user_id = o.user_id
)
SELECT
    channel,
    COUNT(*) AS users,
    SUM(converted) AS converted_users,
    ROUND(SUM(converted)::numeric / NULLIF(COUNT(*), 0), 4) AS conversion_rate,
    ROUND(SUM(revenue)::numeric / NULLIF(SUM(orders), 0), 2) AS aov
FROM joined
GROUP BY channel;

CREATE OR REPLACE VIEW analytics.vw_marketing_efficiency_30d AS
WITH bounds AS (
    SELECT MAX(date) AS max_date
    FROM analytics.dim_date
),
spend AS (
    SELECT
        fms.channel,
        SUM(fms.impressions) AS impressions,
        SUM(fms.clicks) AS clicks,
        SUM(fms.spend) AS spend
    FROM analytics.fact_marketing_spend fms
    JOIN analytics.dim_date dd
        ON fms.date_key = dd.date_key
    CROSS JOIN bounds b
    WHERE dd.date BETWEEN b.max_date - interval '30 days' AND b.max_date
    GROUP BY fms.channel
),
orders AS (
    SELECT
        du.acquisition_channel_proxy AS channel,
        COUNT(DISTINCT fo.user_id) AS converted_users,
        COUNT(DISTINCT fo.order_id) AS orders,
        SUM(fo.revenue) AS revenue
    FROM analytics.fact_orders fo
    JOIN analytics.dim_user du
        ON fo.user_id = du.user_id
    CROSS JOIN bounds b
    WHERE fo.order_date BETWEEN b.max_date - interval '30 days' AND b.max_date
    GROUP BY du.acquisition_channel_proxy
)
SELECT
    s.channel,
    s.impressions,
    s.clicks,
    s.spend,
    o.converted_users,
    o.orders,
    o.revenue,
    ROUND(s.clicks::numeric / NULLIF(s.impressions, 0), 4) AS ctr,
    ROUND(o.converted_users::numeric / NULLIF(s.clicks, 0), 4) AS cvr,
    ROUND(s.spend / NULLIF(o.converted_users, 0), 2) AS cpa,
    ROUND(o.revenue / NULLIF(s.spend, 0), 2) AS roas,
    ROUND(o.revenue / NULLIF(o.orders, 0), 2) AS aov
FROM spend s
LEFT JOIN orders o
    ON s.channel = o.channel;

CREATE OR REPLACE VIEW analytics.vw_cohort_weekly AS
WITH cohort_users AS (
    SELECT
        du.user_id,
        date_trunc('week', du.first_seen_date)::date AS cohort_week
    FROM analytics.dim_user du
),
activity AS (
    SELECT
        cu.user_id,
        cu.cohort_week,
        date_trunc('week', fo.order_date)::date AS activity_week
    FROM cohort_users cu
    JOIN analytics.fact_orders fo
        ON cu.user_id = fo.user_id
),
cohort_sizes AS (
    SELECT cohort_week, COUNT(DISTINCT user_id) AS cohort_size
    FROM cohort_users
    GROUP BY cohort_week
),
cohort_activity AS (
    SELECT
        cohort_week,
        activity_week,
        COUNT(DISTINCT user_id) AS active_users
    FROM activity
    GROUP BY cohort_week, activity_week
)
SELECT
    ca.cohort_week,
    ca.activity_week,
    ((ca.activity_week - ca.cohort_week) / 7) AS weeks_since_signup,
    ca.active_users,
    cs.cohort_size,
    ROUND(ca.active_users::numeric / NULLIF(cs.cohort_size, 0), 4) AS conversion_rate
FROM cohort_activity ca
JOIN cohort_sizes cs
    ON ca.cohort_week = cs.cohort_week;
