CREATE SCHEMA IF NOT EXISTS ml;

CREATE TABLE IF NOT EXISTS ml.runs (
    run_id TEXT PRIMARY KEY,
    snapshot_id TEXT,
    model_name TEXT,
    config_json JSONB,
    git_commit TEXT,
    status TEXT,
    started_at TIMESTAMP,
    finished_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ml.metrics (
    run_id TEXT,
    segment TEXT,
    k INT,
    hit NUMERIC,
    ndcg NUMERIC,
    coverage NUMERIC,
    diversity NUMERIC,
    ci_json JSONB
);

CREATE TABLE IF NOT EXISTS ml.artifacts (
    run_id TEXT,
    artifact_type TEXT,
    uri TEXT,
    checksum TEXT
);
