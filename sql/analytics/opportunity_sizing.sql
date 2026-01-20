-- Opportunity sizing (largest conversion gaps by segment)
-- Replace :start_date and :end_date with YYYY-MM-DD

WITH user_funnel AS (
    SELECT
        du.acquisition_channel_proxy AS channel,
        du.device_proxy AS device,
        fe.user_id,
        MAX(CASE WHEN fe.event_type = 'view' THEN 1 ELSE 0 END) AS has_view,
        MAX(CASE WHEN fe.event_type = 'addtocart' THEN 1 ELSE 0 END) AS has_add_to_cart,
        MAX(CASE WHEN fe.event_type = 'transaction' THEN 1 ELSE 0 END) AS has_purchase
    FROM analytics.fact_events fe
    JOIN analytics.dim_user du
        ON fe.user_id = du.user_id
    WHERE fe.event_date BETWEEN :start_date AND :end_date
    GROUP BY du.acquisition_channel_proxy, du.device_proxy, fe.user_id
),
segment_funnel AS (
    SELECT
        channel,
        device,
        SUM(has_view) AS view_users,
        SUM(has_add_to_cart) AS cart_users,
        SUM(has_purchase) AS purchase_users
    FROM user_funnel
    GROUP BY channel, device
),
segment_orders AS (
    SELECT
        du.acquisition_channel_proxy AS channel,
        du.device_proxy AS device,
        COUNT(DISTINCT fo.order_id) AS orders,
        SUM(fo.revenue) AS revenue
    FROM analytics.fact_orders fo
    JOIN analytics.dim_user du
        ON fo.user_id = du.user_id
    WHERE fo.order_date BETWEEN :start_date AND :end_date
    GROUP BY du.acquisition_channel_proxy, du.device_proxy
),
overall AS (
    SELECT
        SUM(purchase_users)::numeric / NULLIF(SUM(view_users), 0) AS overall_cvr
    FROM segment_funnel
)
SELECT
    sf.channel,
    sf.device,
    sf.view_users,
    sf.cart_users,
    sf.purchase_users,
    ROUND(sf.purchase_users::numeric / NULLIF(sf.view_users, 0), 4) AS view_to_purchase_cvr,
    ROUND(o.overall_cvr - (sf.purchase_users::numeric / NULLIF(sf.view_users, 0)), 4) AS cvr_gap,
    CASE
        WHEN o.overall_cvr > (sf.purchase_users::numeric / NULLIF(sf.view_users, 0))
            THEN ROUND(sf.view_users * (o.overall_cvr - (sf.purchase_users::numeric / NULLIF(sf.view_users, 0)))::numeric, 2)
        ELSE 0
    END AS incremental_orders,
    ROUND(so.revenue / NULLIF(so.orders, 0), 2) AS aov,
    CASE
        WHEN o.overall_cvr > (sf.purchase_users::numeric / NULLIF(sf.view_users, 0))
            THEN ROUND(sf.view_users * (o.overall_cvr - (sf.purchase_users::numeric / NULLIF(sf.view_users, 0))) * (so.revenue / NULLIF(so.orders, 0))::numeric, 2)
        ELSE 0
    END AS incremental_gmv
FROM segment_funnel sf
CROSS JOIN overall o
LEFT JOIN segment_orders so
    ON sf.channel = so.channel AND sf.device = so.device
ORDER BY incremental_orders DESC
LIMIT 20;
