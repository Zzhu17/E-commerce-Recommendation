# DA Insight and Opportunity Sizing Report

Period: 2015-05-03 to 2015-09-18

## Data Coverage
- total_users: 1407580
- total_products: 417053
- total_events: 2756101
- total_orders: 22457

## Funnel Summary (User-level)
| users   | view_users | add_to_cart_users | purchase_users | view_to_cart_cvr | cart_to_purchase_cvr | view_to_purchase_cvr |
| ------- | ---------- | ----------------- | -------------- | ---------------- | -------------------- | -------------------- |
| 1407580 | 1404179    | 37722             | 11719          | 0.0269           | 0.3107               | 0.0083               |

## Segment Performance
| segment_type | segment     | users   | converted_users | conversion_rate | aov   |
| ------------ | ----------- | ------- | --------------- | --------------- | ----- |
| channel      | email       | 351895  | 2958            | 0.0084          | 69.97 |
| channel      | organic     | 351895  | 2923            | 0.0083          | 68.61 |
| channel      | paid_search | 351895  | 2926            | 0.0083          | 68.84 |
| channel      | social      | 351895  | 2912            | 0.0083          | 68.08 |
| country      | BR          | 281516  | 2260            | 0.0080          | 68.07 |
| country      | DE          | 281516  | 2280            | 0.0081          | 69.93 |
| country      | IN          | 281516  | 2427            | 0.0086          | 69.95 |
| country      | UK          | 281516  | 2429            | 0.0086          | 67.67 |
| country      | US          | 281516  | 2323            | 0.0083          | 69.18 |
| device       | Desktop     | 469193  | 4007            | 0.0085          | 70.01 |
| device       | Mobile      | 469194  | 3858            | 0.0082          | 68.25 |
| device       | Tablet      | 469193  | 3854            | 0.0082          | 68.50 |
| user_type    | new         | 1407580 | 11719           | 0.0083          | 68.90 |

## Marketing Efficiency (Proxy)
| channel     | impressions | clicks | spend    | converted_users | orders | revenue   | ctr    | cvr    | cpa  | roas  | aov   |
| ----------- | ----------- | ------ | -------- | --------------- | ------ | --------- | ------ | ------ | ---- | ----- | ----- |
| email       | 677455      | 18531  | 12653.09 | 2958            | 5033   | 352161.98 | 0.0274 | 0.1596 | 4.28 | 27.83 | 69.97 |
| social      | 669942      | 17855  | 12277.54 | 2912            | 4788   | 325954.28 | 0.0267 | 0.1631 | 4.22 | 26.55 | 68.08 |
| organic     | 657136      | 16658  | 11615.04 | 2923            | 3840   | 263472.66 | 0.0253 | 0.1755 | 3.97 | 22.68 | 68.61 |
| paid_search | 659779      | 16288  | 11443.24 | 2926            | 4011   | 276097.37 | 0.0247 | 0.1796 | 3.91 | 24.13 | 68.84 |

## Opportunity Sizing (Top 20)
| channel     | device  | view_users | cart_users | purchase_users | view_to_purchase_cvr | cvr_gap | incremental_orders | aov   | incremental_gmv |
| ----------- | ------- | ---------- | ---------- | -------------- | -------------------- | ------- | ------------------ | ----- | --------------- |
| organic     | Tablet  | 117023     | 3105       | 928            | 0.0079               | 0.0004  | 48.65              | 70.07 | 3409.03         |
| social      | Mobile  | 117036     | 3045       | 942            | 0.0080               | 0.0003  | 34.76              | 66.73 | 2319.55         |
| email       | Mobile  | 116998     | 3141       | 948            | 0.0081               | 0.0002  | 28.44              | 70.42 | 2002.92         |
| social      | Tablet  | 117017     | 3167       | 949            | 0.0081               | 0.0002  | 27.60              | 67.14 | 1853.16         |
| paid_search | Mobile  | 117010     | 3073       | 950            | 0.0081               | 0.0002  | 26.54              | 69.49 | 1844.51         |
| paid_search | Tablet  | 117013     | 3140       | 972            | 0.0083               | 0.0000  | 4.57               | 69.36 | 316.79          |
| paid_search | Desktop | 117027     | 3244       | 1004           | 0.0086               | -0.0002 | 0.0000             | 67.67 | 0.0000          |
| email       | Desktop | 117029     | 3225       | 1005           | 0.0086               | -0.0002 | 0.0000             | 72.41 | 0.0000          |
| organic     | Desktop | 117030     | 3062       | 977            | 0.0083               | 0.0000  | 0.0000             | 69.28 | 0.0000          |
| organic     | Mobile  | 117002     | 3254       | 1018           | 0.0087               | -0.0004 | 0.0000             | 66.60 | 0.0000          |
| social      | Desktop | 117003     | 3118       | 1021           | 0.0087               | -0.0004 | 0.0000             | 70.29 | 0.0000          |
| email       | Tablet  | 116991     | 3148       | 1005           | 0.0086               | -0.0002 | 0.0000             | 67.83 | 0.0000          |

## Notes
- Channel, device, country, and price are deterministic proxies derived from IDs.
- Marketing spend uses proxy CPM/CPC assumptions in `sql/schema/20_build_curated.sql`.
- Use these results for narrative and sizing; do not treat as real marketing attribution.
