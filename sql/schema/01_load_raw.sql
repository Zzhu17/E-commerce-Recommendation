\echo 'Loading RetailRocket raw tables'

\copy raw.events(event_ts_ms, visitor_id, event_type, item_id, transaction_id)
  FROM 'data/rocket/events.csv'
  WITH (FORMAT csv, HEADER true);

\copy raw.item_properties(property_ts_ms, item_id, property, value)
  FROM 'data/rocket/item_properties_part1.csv'
  WITH (FORMAT csv, HEADER true);

\copy raw.item_properties(property_ts_ms, item_id, property, value)
  FROM 'data/rocket/item_properties_part2.csv'
  WITH (FORMAT csv, HEADER true);

\copy raw.category_tree(category_id, parent_id)
  FROM 'data/rocket/category_tree.csv'
  WITH (FORMAT csv, HEADER true);

\echo 'Raw load complete'
