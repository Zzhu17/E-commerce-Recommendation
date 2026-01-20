# E-commerce Recommend Analysis

This project analyzes e-commerce user behavior to quantify conversion funnel performance, cohort conversion, segment differences, marketing efficiency (proxy), and opportunity sizing using the RetailRocket dataset.

## What Was Analyzed
- Funnel: view -> addtocart -> transaction
- Cohort conversion: weekly cohorts by first_seen_date
- Segmentation: channel/device/country/new vs returning (proxy dimensions)
- Marketing efficiency: CTR/CVR/CPA/ROAS (proxy spend)
- Opportunity sizing: incremental orders and GMV by segment gap

## Data and Modeling
- Source data: `data/rocket/` (events, item properties, category tree)
- Warehouse: PostgreSQL star schema in `analytics` schema
  - `dim_user`, `dim_product`, `dim_date`, `dim_campaign`
  - `fact_events`, `fact_orders`, `fact_marketing_spend`
- Proxy assumptions (documented in `docs/da_mapping.md`):
  - channel/device/country derived from user_id
  - product price derived from item_id
  - marketing spend from CPM/CPC constants

## Implementation
- Raw load + curated build: `sql/schema/`
- Analysis SQL: `sql/analytics/`
- Dashboard views: `sql/analytics/dashboard_views.sql`
- Power BI extracts: `dashboards/powerbi/extracts/`
- DAX template: `docs/dax_measures_template.md`
- Power BI screenshots: `e-commerce-recommend.pdf`

## Results (RetailRocket 2015-05-03 to 2015-09-18)
- Coverage: 1,407,580 users, 417,053 products, 2,756,101 events, 22,457 orders
- Funnel (user-level):
  - view_to_cart_cvr: 2.69%
  - cart_to_purchase_cvr: 31.07%
  - view_to_purchase_cvr: 0.83%
- Segment highlights (proxy):
  - Channel CVR ~0.83% (email highest at 0.84%)
  - Device CVR: Desktop 0.85% vs Mobile/Tablet 0.82%
  - Country CVR: UK/IN 0.86% highest
- Marketing efficiency (proxy):
  - ROAS range: 22.68 to 27.83
  - CPA range: 3.91 to 4.28
- Opportunity sizing (proxy):
  - Top gap segment: organic + tablet
  - Incremental orders: 48.65
  - Incremental GMV: 3409.03

Detailed tables and methodology are in `docs/insights_report.md` and `sql/analytics/opportunity_sizing.sql`.

## How to Run

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

If you do not have `psql` installed, run the Python loader:
```bash
python src/data/load_rocket_postgres.py
```

Export Power BI extracts:
```bash
python src/analytics/export_dashboard.py
```

## Deliverables
- Insight report: `docs/insights_report.md`
- Dashboard spec: `docs/dashboard_spec.md`
- DAX template: `docs/dax_measures_template.md`
- Power BI screenshots: `e-commerce-recommend.pdf`

## Analysis Outcome
- Funnel performance: view->purchase CVR ~0.83%, view->addtocart 2.69%, addtocart->purchase 31.07%; main drop-off happens at view->addtocart.
- Channel differences (proxy): overall CVR ~0.83%, email slightly higher (0.84%); channel-level uplift is limited without finer segmentation.
- Device differences (proxy): Desktop CVR 0.85% vs Mobile/Tablet 0.82%; mobile has room for UX/performance improvements.
- Country differences (proxy): UK/IN CVR 0.86% vs BR 0.80%; suggests regional optimization opportunities.
- Marketing efficiency (proxy): ROAS 22.68-27.83, CPA 3.91-4.28; email and social look stronger.
- Opportunity sizing (proxy): top gap segment is organic + tablet with ~48.65 incremental orders and ~3409 incremental GMV.
- Proxy caveat: RetailRocket lacks real marketing spend/device/country; these fields are simulated for directional insights and should not drive real budget allocation or attribution decisions.
