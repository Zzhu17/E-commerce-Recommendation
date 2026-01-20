#!/usr/bin/env bash
set -euo pipefail

DB_URL=${DATABASE_URL:-"postgresql://localhost:5432/rocket"}

psql "$DB_URL" -f sql/schema/00_raw_tables.sql
psql "$DB_URL" -f sql/schema/01_load_raw.sql
psql "$DB_URL" -f sql/schema/10_curated_tables.sql
psql "$DB_URL" -f sql/schema/20_build_curated.sql
psql "$DB_URL" -f sql/analytics/dashboard_views.sql

echo "Load complete"
