CREATE SCHEMA IF NOT EXISTS dq;

CREATE TABLE IF NOT EXISTS dq.validation_results (
    validation_id TEXT,
    suite_name TEXT,
    run_at TIMESTAMP,
    success BOOLEAN,
    result_json JSONB
);
