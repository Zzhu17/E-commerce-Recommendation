CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.events (
    event_ts_ms BIGINT,
    visitor_id BIGINT,
    event_type TEXT,
    item_id BIGINT,
    transaction_id BIGINT
);

CREATE TABLE IF NOT EXISTS raw.item_properties (
    property_ts_ms BIGINT,
    item_id BIGINT,
    property TEXT,
    value TEXT
);

CREATE TABLE IF NOT EXISTS raw.category_tree (
    category_id BIGINT,
    parent_id BIGINT
);

CREATE INDEX IF NOT EXISTS idx_raw_events_visitor_ts
    ON raw.events (visitor_id, event_ts_ms);

CREATE INDEX IF NOT EXISTS idx_raw_events_item
    ON raw.events (item_id);

CREATE INDEX IF NOT EXISTS idx_raw_item_properties_item
    ON raw.item_properties (item_id);

CREATE INDEX IF NOT EXISTS idx_raw_item_properties_property
    ON raw.item_properties (property);
