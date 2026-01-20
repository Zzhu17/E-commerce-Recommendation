-- Funnel analysis (user-level)
-- Replace :start_date and :end_date with YYYY-MM-DD

WITH base AS (
    SELECT
        fe.user_id,
        MAX(CASE WHEN fe.event_type = 'view' THEN 1 ELSE 0 END) AS has_view,
        MAX(CASE WHEN fe.event_type = 'addtocart' THEN 1 ELSE 0 END) AS has_add_to_cart,
        MAX(CASE WHEN fe.event_type = 'transaction' THEN 1 ELSE 0 END) AS has_purchase
    FROM analytics.fact_events fe
    WHERE fe.event_date BETWEEN :start_date AND :end_date
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
