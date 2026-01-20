# Power BI DAX Measures Template

Use these measures to avoid accidental SUM on rates. Adjust table names if you renamed sources.

## Funnel (vw_funnel_30d)
```DAX
Users = MAX(vw_funnel_30d[users])
View Users = MAX(vw_funnel_30d[view_users])
Add To Cart Users = MAX(vw_funnel_30d[add_to_cart_users])
Purchasers = MAX(vw_funnel_30d[purchase_users])
View to Cart CVR = MAX(vw_funnel_30d[view_to_cart_cvr])
Cart to Purchase CVR = MAX(vw_funnel_30d[cart_to_purchase_cvr])
View to Purchase CVR = MAX(vw_funnel_30d[view_to_purchase_cvr])
```

## Marketing (vw_marketing_efficiency_30d)
```DAX
ROAS Avg = AVERAGE(vw_marketing_efficiency_30d[roas])
CPA Avg = AVERAGE(vw_marketing_efficiency_30d[cpa])
CTR Avg = AVERAGE(vw_marketing_efficiency_30d[ctr])
CVR Avg = AVERAGE(vw_marketing_efficiency_30d[cvr])
AOV Avg = AVERAGE(vw_marketing_efficiency_30d[aov])
```

## Segment (vw_segment_channel_30d)
```DAX
Segment Conversion Rate = AVERAGE(vw_segment_channel_30d[conversion_rate])
Segment AOV = AVERAGE(vw_segment_channel_30d[aov])
```

## Cohort (vw_cohort_weekly)
```DAX
Cohort Conversion Rate = AVERAGE(vw_cohort_weekly[conversion_rate])
```

## Optional Funnel Stage Table + Measure
```DAX
FunnelStage = DATATABLE(
    "Stage", STRING,
    { {"View"}, {"Add to Cart"}, {"Purchase"} }
)

Stage Count =
SWITCH(
    SELECTEDVALUE(FunnelStage[Stage]),
    "View", [View Users],
    "Add to Cart", [Add To Cart Users],
    "Purchase", [Purchasers]
)
```
