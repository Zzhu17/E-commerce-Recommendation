# RetailRocket -> Star Schema Mapping (DA Phase 1)

## Source tables
- data/rocket/events.csv
  - timestamp (ms), visitorid, event, itemid, transactionid
  - event values: view, addtocart, transaction
- data/rocket/item_properties_part1.csv / part2.csv
  - timestamp (ms), itemid, property, value
  - property includes categoryid and other attributes
- data/rocket/category_tree.csv
  - categoryid, parentid

## Target star schema
### dim_user
- user_id: events.visitorid
- first_seen_ts: MIN(events.timestamp)
- first_seen_date: date(first_seen_ts)
- country_proxy: derived from hash(user_id)
- device_proxy: derived from hash(user_id)
- acquisition_channel_proxy: derived from hash(user_id)

### dim_product
- product_id: itemid
- category_id: latest item_properties.categoryid
- parent_category_id: category_tree.parentid
- price_proxy: deterministic price derived from product_id

### dim_date
- date_key: YYYYMMDD
- date, year, month, week, day_of_week
- generated from min/max events date

### fact_events
- event_ts: to_timestamp(events.timestamp / 1000)
- event_date: date(event_ts)
- user_id: visitorid
- product_id: itemid
- event_type: event
- transaction_id: transactionid
- session_id: derived (30-min inactivity split per user)

### fact_orders
- order_id: transactionid
- order_ts: event_ts
- user_id, product_id
- quantity: 1 (proxy)
- unit_price: dim_product.price_proxy
- discount: 0.0 (proxy)
- revenue: quantity * unit_price

### dim_campaign (proxy)
- campaign_id: channel name (text)
- channel: {organic, paid_search, social, email}
- campaign_name: channel-based default
- start_date/end_date: data range

### fact_marketing_spend (proxy)
- date_key, campaign_id, channel
- impressions: count(view events)
- clicks: count(addtocart events) as click proxy
- spend: impressions * CPM + clicks * CPC (constants)

## Proxy assumptions (explicit)
- No real marketing data exists in RetailRocket. We create channel and spend proxies for DA storytelling only.
- No device/country fields exist. We create deterministic proxies from user_id to enable segmentation.
- No product price exists. We create a stable price proxy from product_id for AOV/GMV calculations.
- Funnel mapping uses:
  - view -> addtocart -> transaction
  - addtocart is treated as click equivalent in marketing metrics.
