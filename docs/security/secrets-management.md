# Secrets Management Standard

## 1) Injection only (no plaintext in code/config)
- `backend/src/main/resources/application.yml` and compose files now read sensitive values from environment variables.
- Do **not** commit any `.env*` files.
- Use one of these providers per environment:
  - **dev**: inject via local shell/session secret manager export.
  - **staging/prod**: Vault / cloud KMS + workload identity / Kubernetes Secret.

## 2) Production deployment source of truth
For `docker-compose.prod.yml`, variables must be injected by runtime platform (not stored in repo):
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `API_AUTH_KEY`, `API_AUTH_ADMIN_KEY`
- `SPRING_DATASOURCE_*`

Suggested mappings:
- Vault KV path: `reco/<env>/backend/*`
- AWS: Secrets Manager + KMS CMK
- GCP: Secret Manager + CMEK
- K8s: External Secrets Operator -> namespaced `Secret`

## 3) Independent keys per environment
Use separate key sets for each environment:
- `dev`: `reco/dev/api_auth_key`, `reco/dev/api_auth_admin_key`, `reco/dev/db_password`
- `staging`: `reco/staging/...`
- `prod`: `reco/prod/...`

Never reuse keys across environments.

## 4) Rotation & expiration policy
- API keys: rotate every **30 days**; max TTL **45 days**.
- DB passwords: rotate every **60 days**; max TTL **90 days**.
- Emergency rotation SLA: **< 4 hours** after leak suspicion.
- Keep previous key valid for a short overlap window (e.g., 24h) to support zero-downtime rollout.

## 5) Logging / response / UI safety
- Never log secrets or auth headers (`x-api-key`, `x-admin-key`, bearer tokens, DB password).
- Error responses must stay generic (`INTERNAL_ERROR`, no stack trace or secret value).
- Frontend must not echo backend error body that might contain secret-like values.

## 6) CI gate
- CI runs gitleaks in pull requests and pushes; leaks fail the build.
