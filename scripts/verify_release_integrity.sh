#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <image-ref> [image-ref ...]" >&2
  exit 1
fi

for image_ref in "$@"; do
  if [[ "$image_ref" != *@sha256:* ]]; then
    echo "Image must use immutable digest reference: $image_ref" >&2
    exit 1
  fi

  cosign verify \
    --certificate-identity-regexp 'https://github.com/.+/.+/.github/workflows/.+' \
    --certificate-oidc-issuer https://token.actions.githubusercontent.com \
    "$image_ref" >/dev/null

  echo "Verified signature and provenance: $image_ref"
done
