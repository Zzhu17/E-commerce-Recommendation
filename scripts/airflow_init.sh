#!/usr/bin/env bash
set -euo pipefail

if command -v docker-compose >/dev/null 2>&1; then
  docker-compose up -d postgres minio airflow
else
  docker compose up -d postgres minio airflow
fi

echo "Airflow initialized. UI: http://localhost:8080 (admin/admin)"
