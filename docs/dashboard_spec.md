# Dashboard Template Spec (Power BI)

## Data Sources (CSV extracts)
- `dashboards/powerbi/extracts/funnel_30d.csv`
- `dashboards/powerbi/extracts/segment_channel_30d.csv`
- `dashboards/powerbi/extracts/marketing_efficiency_30d.csv`
- `dashboards/powerbi/extracts/cohort_weekly.csv`

## Field List
### funnel_30d
- users
- view_users
- add_to_cart_users
- purchase_users
- view_to_cart_cvr
- cart_to_purchase_cvr
- view_to_purchase_cvr

### segment_channel_30d
- channel
- users
- converted_users
- conversion_rate
- aov

### marketing_efficiency_30d
- channel
- impressions
- clicks
- spend
- converted_users
- orders
- revenue
- ctr
- cvr
- cpa
- roas
- aov

### cohort_weekly
- cohort_week
- activity_week
- weeks_since_signup
- active_users
- cohort_size
- conversion_rate

## Dashboard Layouts
### Dashboard 1: Funnel and Conversion
- KPI tiles (top row)
  - Users (users)
  - Purchasers (purchase_users)
  - View to Purchase CVR (view_to_purchase_cvr)
  - AOV (from segment_channel_30d, overall weighted)
- Funnel chart (view_users -> add_to_cart_users -> purchase_users)
- Conversion rate bar chart
  - view_to_cart_cvr
  - cart_to_purchase_cvr

### Dashboard 2: Marketing and Segments
- Channel performance table (channel, conversion_rate, aov)
- Marketing efficiency bar chart
  - ROAS by channel
  - CPA by channel
- Segment distribution (optional)
  - Users by channel

### Dashboard 3: Cohort Retention
- Cohort heatmap
  - Rows: cohort_week
  - Columns: weeks_since_signup
  - Color: conversion_rate
- Line chart (optional)
  - cohort_size vs time

## Recommended Aggregations

### vw_funnel_30d
| Field | Aggregation |
| --- | --- |
| users | Sum |
| view_users | Sum |
| add_to_cart_users | Sum |
| purchase_users | Sum |
| view_to_cart_cvr | Average or Don't summarize |
| cart_to_purchase_cvr | Average or Don't summarize |
| view_to_purchase_cvr | Average or Don't summarize |

### vw_segment_channel_30d
| Field | Aggregation |
| --- | --- |
| users | Sum |
| converted_users | Sum |
| conversion_rate | Average or Don't summarize |
| aov | Average or Don't summarize |

### vw_marketing_efficiency_30d
| Field | Aggregation |
| --- | --- |
| impressions | Sum |
| clicks | Sum |
| spend | Sum |
| converted_users | Sum |
| orders | Sum |
| revenue | Sum |
| ctr | Average or Don't summarize |
| cvr | Average or Don't summarize |
| cpa | Average or Don't summarize |
| roas | Average or Don't summarize |
| aov | Average or Don't summarize |

### vw_cohort_weekly
| Field | Aggregation |
| --- | --- |
| cohort_week | Use as row axis (no aggregation) |
| activity_week | Use as column axis (no aggregation) |
| weeks_since_signup | Use as column axis (no aggregation) |
| active_users | Sum |
| cohort_size | Sum |
| conversion_rate | Average or Don't summarize |

## Notes
- If you want daily or weekly trends, connect directly to `analytics.fact_events` and `analytics.fact_orders`.
- Use the 30-day views for a clean snapshot; use full SQL in `sql/analytics/` for custom ranges.
