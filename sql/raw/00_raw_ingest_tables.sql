CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.ingest_batches (
    batch_id TEXT PRIMARY KEY,
    dataset TEXT NOT NULL,
    dataset_version TEXT,
    downloaded_at TIMESTAMP,
    manifest_json JSONB
);

CREATE TABLE IF NOT EXISTS raw.ingest_files (
    batch_id TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    file_size BIGINT,
    PRIMARY KEY (batch_id, file_name)
);

CREATE TABLE IF NOT EXISTS raw.events_raw (
    batch_id TEXT NOT NULL,
    event_ts_ms BIGINT,
    visitor_id BIGINT,
    event_type TEXT,
    item_id BIGINT,
    transaction_id BIGINT
);

CREATE TABLE IF NOT EXISTS raw.item_properties_raw (
    batch_id TEXT NOT NULL,
    property_ts_ms BIGINT,
    item_id BIGINT,
    property TEXT,
    value TEXT
);

CREATE TABLE IF NOT EXISTS raw.category_tree_raw (
    batch_id TEXT NOT NULL,
    category_id BIGINT,
    parent_id BIGINT
);

CREATE INDEX IF NOT EXISTS idx_events_raw_batch ON raw.events_raw (batch_id);
CREATE INDEX IF NOT EXISTS idx_item_props_raw_batch ON raw.item_properties_raw (batch_id);
CREATE INDEX IF NOT EXISTS idx_category_raw_batch ON raw.category_tree_raw (batch_id);
