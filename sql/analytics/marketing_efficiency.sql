-- Marketing efficiency (proxy)
-- Replace :start_date and :end_date with YYYY-MM-DD

WITH spend AS (
    SELECT
        fms.channel,
        SUM(fms.impressions) AS impressions,
        SUM(fms.clicks) AS clicks,
        SUM(fms.spend) AS spend
    FROM analytics.fact_marketing_spend fms
    JOIN analytics.dim_date dd
        ON fms.date_key = dd.date_key
    WHERE dd.date BETWEEN :start_date AND :end_date
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
    WHERE fo.order_date BETWEEN :start_date AND :end_date
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
    ON s.channel = o.channel
ORDER BY s.spend DESC;
