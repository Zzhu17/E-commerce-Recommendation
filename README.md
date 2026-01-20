# ConversionOps (RetailRocket)

ConversionOps uses user behavior events to build a conversion funnel, cohort analysis, and opportunity sizing. Phase 1 is DA-first; DS/SWE/DE layers can be added later without changing the data model.

## Data Sources (RetailRocket)
- `data/rocket/events.csv` (view, addtocart, transaction)
- `data/rocket/item_properties_part1.csv`
- `data/rocket/item_properties_part2.csv`
- `data/rocket/category_tree.csv`

## DA Deliverables (Phase 1)
- Star schema in PostgreSQL (facts + dimensions)
- Metric system: funnel, cohort, segment, marketing efficiency
- 1-2 dashboards (Power BI) using exported extracts
- Opportunity sizing report (method in this README)
- Insight report: `docs/insights_report.md`
- Dashboard spec: `docs/dashboard_spec.md`
- DAX template: `docs/dax_measures_template.md`
- Power BI screenshots (PDF): `e-commerce-recommend.pdf`

## Data Model (Star Schema)
See `docs/da_mapping.md` for full mapping and proxy assumptions.

Core tables in the `analytics` schema:
- `dim_user` (includes country/device/channel proxies)
- `dim_product` (category + price proxy)
- `dim_date`
- `fact_events`
- `fact_orders`
- `fact_marketing_spend` (proxy)
- `dim_campaign` (proxy)

## Quick Start (PostgreSQL)

Start Postgres with Docker:
```bash
docker compose up -d postgres
```

Set a database connection string:
```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/rocket"
```

Load raw data, build curated tables, and create dashboard views:
```bash
scripts/load_rocket_postgres.sh
```

If you do not have `psql` installed, run the Python loader (uses COPY for speed):
```bash
python src/data/load_rocket_postgres.py
```

Export dashboard extracts for Power BI:
```bash
python src/analytics/export_dashboard.py
```

Exports are written to `dashboards/powerbi/extracts`.

## Metric Dictionary (DA)
- Funnel: view -> addtocart -> transaction
- Conversion rates:
  - view_to_cart_cvr = add_to_cart_users / view_users
  - cart_to_purchase_cvr = purchase_users / add_to_cart_users
  - view_to_purchase_cvr = purchase_users / view_users
- Cohort: weekly cohorts based on `first_seen_date`, conversion measured by weekly purchase activity
- Segmentation: channel/device/country/new vs returning
- Marketing efficiency (proxy):
  - CTR = clicks / impressions (addtocart as click proxy)
  - CVR = converted_users / clicks
  - CPA = spend / converted_users
  - ROAS = revenue / spend
  - AOV = revenue / orders

All query definitions live in `sql/analytics/`.

## Opportunity Sizing Method
We identify segments with the largest conversion gap vs overall rate and estimate upside:

```
incremental_orders = view_users * max(0, target_cvr - segment_cvr)
incremental_gmv = incremental_orders * AOV
```

- Default target is the overall conversion rate for the same period.
- See `sql/analytics/opportunity_sizing.sql` for the calculation.

## Dashboard-Ready Views
`sql/analytics/dashboard_views.sql` creates:
- `analytics.vw_funnel_30d`
- `analytics.vw_segment_channel_30d`
- `analytics.vw_marketing_efficiency_30d`
- `analytics.vw_cohort_weekly`

These views power the CSV extracts for BI tools.

## Repo Layout (DA-focused)
```
conversionops/
  docs/da_mapping.md
  sql/
    schema/                 # raw + curated tables
    analytics/              # funnel/cohort/segment/opportunity
  src/
    data/load_rocket_postgres.py
    analytics/export_dashboard.py
  dashboards/powerbi/extracts/
```

## Notes on Proxies
RetailRocket does not provide marketing spend, device, or country. We create deterministic proxies from user_id and item_id. All proxies are documented in `docs/da_mapping.md` and are meant for analysis narrative only.

## Next Steps (optional)
- Add ML propensity scoring and recommendation models
- Serve metrics via FastAPI
- Orchestrate daily ETL in Airflow
