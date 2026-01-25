#!/usr/bin/env bash
set -euo pipefail

DB_URL=${DATABASE_URL:-"postgresql://rocket:Zzp990812@localhost:5434/rocket"}

# Start Postgres via docker-compose
if command -v docker-compose >/dev/null 2>&1; then
  docker-compose up -d postgres
else
  docker compose up -d postgres
fi

# Wait for readiness
for i in {1..30}; do
  if pg_isready -d "$DB_URL" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

# Load schema + data
DATABASE_URL="$DB_URL" python src/data/load_rocket_postgres.py

# Write data fingerprint for reproducibility
python experiments/data_fingerprint.py

echo "Postgres ready: $DB_URL"
