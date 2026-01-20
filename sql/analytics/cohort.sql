-- Cohort conversion by weeks since first_seen
-- Replace :start_date and :end_date with YYYY-MM-DD

WITH cohort_users AS (
    SELECT
        du.user_id,
        date_trunc('week', du.first_seen_date)::date AS cohort_week
    FROM analytics.dim_user du
    WHERE du.first_seen_date BETWEEN :start_date AND :end_date
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
    ON ca.cohort_week = cs.cohort_week
ORDER BY ca.cohort_week, ca.activity_week;
