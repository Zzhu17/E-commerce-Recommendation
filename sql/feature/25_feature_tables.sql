CREATE SCHEMA IF NOT EXISTS feat;

CREATE TABLE IF NOT EXISTS feat.feature_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    ds DATE,
    train_range TEXT,
    test_range TEXT,
    logic_version TEXT,
    data_hash TEXT,
    counts_json JSONB
);

CREATE TABLE IF NOT EXISTS feat.id_mappings (
    snapshot_id TEXT,
    user_id BIGINT,
    user_idx INT,
    item_id BIGINT,
    item_idx INT
);

CREATE TABLE IF NOT EXISTS feat.train_edges (
    snapshot_id TEXT,
    user_idx INT,
    item_idx INT,
    weight NUMERIC
);

CREATE TABLE IF NOT EXISTS feat.holdout_truth (
    snapshot_id TEXT,
    user_idx INT,
    item_idx INT
);
