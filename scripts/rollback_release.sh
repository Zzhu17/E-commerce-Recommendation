#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <backend_image_digest_ref> <model_api_image_digest_ref>" >&2
  exit 1
fi

backend_image="$1"
model_api_image="$2"

if [[ "$backend_image" != *@sha256:* ]] || [[ "$model_api_image" != *@sha256:* ]]; then
  echo "Rollback images must be immutable digest references (@sha256:...)." >&2
  exit 1
fi

export BACKEND_IMAGE="$backend_image"
export MODEL_API_IMAGE="$model_api_image"

echo "Rolling back backend to $BACKEND_IMAGE"
echo "Rolling back model-api to $MODEL_API_IMAGE"

docker compose -f docker-compose.prod.yml -f ops/release/docker-compose.release.yml pull backend model-api
docker compose -f docker-compose.prod.yml -f ops/release/docker-compose.release.yml up -d backend model-api

echo "Rollback completed."
