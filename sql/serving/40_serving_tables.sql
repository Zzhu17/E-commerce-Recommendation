CREATE SCHEMA IF NOT EXISTS serving;

CREATE TABLE IF NOT EXISTS serving.reco_candidates (
    model_version TEXT,
    user_id BIGINT,
    rank INT,
    item_id BIGINT,
    score NUMERIC,
    generated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS serving.model_releases (
    name TEXT PRIMARY KEY,
    active_model_version TEXT,
    updated_at TIMESTAMP
);
