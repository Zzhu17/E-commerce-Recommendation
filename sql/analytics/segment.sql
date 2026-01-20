-- Segment conversion metrics
-- Replace :start_date and :end_date with YYYY-MM-DD

WITH user_base AS (
    SELECT
        du.user_id,
        du.country_proxy,
        du.device_proxy,
        du.acquisition_channel_proxy,
        CASE WHEN du.first_seen_date BETWEEN :start_date AND :end_date
            THEN 'new'
            ELSE 'returning'
        END AS user_type
    FROM analytics.dim_user du
),
orders AS (
    SELECT
        fo.user_id,
        COUNT(DISTINCT fo.order_id) AS orders,
        SUM(fo.revenue) AS revenue
    FROM analytics.fact_orders fo
    WHERE fo.order_date BETWEEN :start_date AND :end_date
    GROUP BY fo.user_id
),
joined AS (
    SELECT
        ub.*,
        COALESCE(o.orders, 0) AS orders,
        COALESCE(o.revenue, 0.0) AS revenue,
        CASE WHEN COALESCE(o.orders, 0) > 0 THEN 1 ELSE 0 END AS converted
    FROM user_base ub
    LEFT JOIN orders o
        ON ub.user_id = o.user_id
)
SELECT
    'channel' AS segment_type,
    acquisition_channel_proxy AS segment,
    COUNT(*) AS users,
    SUM(converted) AS converted_users,
    ROUND(SUM(converted)::numeric / NULLIF(COUNT(*), 0), 4) AS conversion_rate,
    ROUND(SUM(revenue)::numeric / NULLIF(SUM(orders), 0), 2) AS aov
FROM joined
GROUP BY acquisition_channel_proxy

UNION ALL

SELECT
    'device' AS segment_type,
    device_proxy AS segment,
    COUNT(*) AS users,
    SUM(converted) AS converted_users,
    ROUND(SUM(converted)::numeric / NULLIF(COUNT(*), 0), 4) AS conversion_rate,
    ROUND(SUM(revenue)::numeric / NULLIF(SUM(orders), 0), 2) AS aov
FROM joined
GROUP BY device_proxy

UNION ALL

SELECT
    'country' AS segment_type,
    country_proxy AS segment,
    COUNT(*) AS users,
    SUM(converted) AS converted_users,
    ROUND(SUM(converted)::numeric / NULLIF(COUNT(*), 0), 4) AS conversion_rate,
    ROUND(SUM(revenue)::numeric / NULLIF(SUM(orders), 0), 2) AS aov
FROM joined
GROUP BY country_proxy

UNION ALL

SELECT
    'user_type' AS segment_type,
    user_type AS segment,
    COUNT(*) AS users,
    SUM(converted) AS converted_users,
    ROUND(SUM(converted)::numeric / NULLIF(COUNT(*), 0), 4) AS conversion_rate,
    ROUND(SUM(revenue)::numeric / NULLIF(SUM(orders), 0), 2) AS aov
FROM joined
GROUP BY user_type

ORDER BY segment_type, segment;
