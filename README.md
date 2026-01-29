# E-Commerce Recommendation (Offline Evaluation)

Status:
- Offline recommendation evaluation complete
- Baseline vs model comparison implemented
- Metrics focus on business-aligned proxy indicators

---

## Table of Contents
- [DA (Analytics)](#da-analytics)
  - [Business Objective](#business-objective)
  - [Scope & Constraints](#scope--constraints)
  - [Data Description](#data-description)
  - [Evaluation Metrics (Offline Proxies)](#evaluation-metrics-offline-proxies)
  - [Results Summary (Sampled Offline Evaluation)](#results-summary-sampled-offline-evaluation)
  - [Trade-offs & Observations](#trade-offs--observations)
  - [Limitations & Next Steps](#limitations--next-steps)
- [DS (Data Science)](#ds-data-science)
  - [Recommendation Approaches](#recommendation-approaches)
  - [Project Navigation (Step1/Step2/Step3)](#project-navigation-step1step2step3)
  - [Modern Recommenders (LightGCN + ALS)](#modern-recommenders-lightgcn--als)
  - [Experiment Framework (DS)](#experiment-framework-ds)
- [DE (Data Engineering)](#de-data-engineering)
  - [Reproducibility (Data + Schema)](#reproducibility-data--schema)
  - [DE Pipeline (Airflow)](#de-pipeline-airflow)
- [Full-Stack (Frontend + Spring + Model API)](#full-stack-frontend--spring--model-api)
  - [Online System Summary](#online-system-summary)
  - [How to Run (Production Compose)](#how-to-run-production-compose)
  - [How to Run (Local Dev)](#how-to-run-local-dev)
  - [API Contract Draft (Frontend + Spring + Python)](#api-contract-draft-frontend--spring--python)
  - [Latest Integration Test (January 29, 2026)](#latest-integration-test-january-29-2026)

## DA (Analytics)
### Business Objective
This project evaluates an e-commerce product recommendation strategy in an offline setting.

The recommendation system is designed to:
- Improve product discovery
- Increase user engagement
- Support downstream business metrics such as click-through rate and conversion rate

Given data constraints, the focus is on pre-deployment evaluation rather than online experimentation.

### Scope & Constraints
This project focuses on offline recommendation evaluation due to the absence of real-time user
interaction signals such as impressions, clicks, or purchases after recommendation exposure.

As a result:
- Online A/B testing is not performed
- Model performance is evaluated using offline proxy metrics
- Results are interpreted as potential uplift rather than guaranteed production impact

This reflects a common early-stage evaluation process in real-world recommendation systems.

### Data Description
- User-item interactions derived from historical events in RetailRocket
- Implicit feedback assumption: past interactions indicate relevance
- No negative feedback is explicitly observed
- Evaluation uses a temporal split to reduce information leakage

### Evaluation Metrics (Offline Proxies)
Given the offline setting, the following metrics are used as business-aligned proxies:

- Hit@K: whether a relevant item appears in the top-K recommendations
- NDCG@K: rewards higher-ranked hits, closer to online ranking quality
- Coverage: proportion of unique items recommended across all users
- Diversity: average category variety within each user's top-K list

These metrics serve as proxies for online engagement, product discovery, and exploration.

### Results Summary (Sampled Offline Evaluation)
Configuration: temporal split with sampled users (sample_mod in {50,100,200}), candidate pool in
{1k,2k,5k}, K in {5,10,20}. Robustness grid includes bootstrap CIs and stability across 81
configurations.

| Metric | Popularity Baseline | Collaborative Filtering |
| --- | --- | --- |
| Hit@K (avg) | 0.2183 | 0.0000 |
| NDCG@10 (single) | 0.0944 | 0.0000 |
| Coverage@K (avg) | 0.0070 | 0.0210 |
| Diversity@K (avg) | 0.5574 | 0.9006 |

The collaborative filtering model increases coverage and diversity, indicating broader catalog
exposure, while underperforming the popularity baseline on Hit@K and NDCG@10 in this sample.
This suggests that popularity remains a strong baseline on sparse interaction data and that
personalization may require richer signals or hybrid strategies.

Interleaving check (popularity vs hybrid) shows lower NDCG@10 for the interleaved list
(0.0334) than popularity (0.0944) in the current sample, indicating hybrid needs stronger
personalization signals before deployment.

Single-run sanity check (seed=42, sample_mod=200, candidate_size=2000, K=10): NDCG@10
popularity 0.0944, collaborative filtering 0.0000

### Trade-offs & Observations
- Better coverage/diversity can come at the cost of lower Hit@K
- This highlights the balance between recommendation accuracy and exploration
- In production systems, hybrid ranking or exploration-aware strategies are often used

### Limitations & Next Steps
- Offline metrics do not guarantee online performance
- No user feedback loop is available
- Future work may include:
  - Online A/B testing
  - Exploration strategies (epsilon-greedy, Thompson sampling)
  - Hybrid recommendation approaches

---

## DS (Data Science)
### Recommendation Approaches
#### Baseline: Popularity-Based Recommendation
- Items ranked by overall interaction frequency
- Same recommendation list for all users
- Serves as a simple, interpretable benchmark

#### Baseline: Time-Decayed Popularity
- Items ranked by recency-weighted interaction frequency
- Prioritizes recent trends over older interactions

#### Model: Collaborative Filtering (User-Based)
- Learns user-item interaction patterns
- Produces personalized recommendation lists
- Captures latent preferences beyond popularity bias

#### Hybrid Decision Rule (Segmented)
- cold users -> popularity
- light users -> time-decayed popularity
- heavy users -> user_cf

### Project Navigation (Step1/Step2/Step3)
Step 1: Robustness grid + summary
- Run: `DATABASE_URL=... python experiments/run_experiments.py`
- Outputs: `artifacts/experiments/<run_id>/results.csv`, `results.parquet`, `plots/`, `summary.md`

Step 2: Ranking metrics + segmentation + diagnostics
- NDCG@K added in `src/evaluation/metrics.py`
- Segment results in `artifacts/experiments/<run_id>/segment_results.csv`
- Diagnostics in `docs/data_diagnostics.md`

Step 3: Sanity check + interleaving + reproducibility
- Single eval (auto-patches README): `DATABASE_URL=... python experiments/single_eval.py`
- Interleaving results: `artifacts/experiments/interleaving_results.csv`
- Data fingerprint: `python experiments/data_fingerprint.py` (also embedded in `manifest.json`)

### Modern Recommenders (LightGCN + ALS)
- LightGCN training: `DATABASE_URL=... python experiments/train_lightgcn.py`
- ALS baseline: `DATABASE_URL=... python experiments/train_als.py`
- Graph/mappings: `DATABASE_URL=... python experiments/build_graph.py`
- Event weighting toggle: set `eval.event_weighting: true` in `experiments/configs/base.yaml`

### Experiment Framework (DS)
Batch experiments generate a full artifact bundle per run:
- `artifacts/experiments/<run_id>/results.parquet`
- `artifacts/experiments/<run_id>/results.csv`
- `artifacts/experiments/<run_id>/summary.md`
- `artifacts/experiments/<run_id>/plots/*.png`
- `artifacts/experiments/<run_id>/manifest.json`

Config templates:
- `experiments/configs/base.yaml`
- `experiments/configs/grid_small.yaml`

Run a grid:
```bash
python experiments/run_experiments.py
python experiments/summarize_results.py
```

Diagnostics and hypotheses:
```bash
python experiments/data_diagnostics.py
```
Artifacts:
- `docs/data_diagnostics.md`
- `docs/online_hypotheses.md`
- `docs/ground_truth.md`

Step 3 extras:
```bash
python experiments/single_eval.py
python experiments/data_fingerprint.py
```

Offline evaluation:
```bash
export DATABASE_URL="postgresql://rocket:Zzp990812@localhost:5434/rocket"
RECO_SAMPLE_MOD=200 python experiments/single_eval.py
```

Outputs:
- `ecommerce-recommend.pdf` (Power BI dashboard screenshots)
- `docs/ground_truth.md`
- `artifacts/data_fingerprint.json`
- `artifacts/experiments/interleaving_results.csv`
- `artifacts/experiments/20260125_102952/` (latest grid run artifacts)

---

## DE (Data Engineering)
### Reproducibility (Data + Schema)
Quickstart (DB + schema + data):
```bash
./scripts/bootstrap_postgres.sh
```

Dataset download (optional):
```bash
python -c "import kagglehub; print(kagglehub.dataset_download('retailrocket/ecommerce-dataset'))"
```
If the dataset is stored elsewhere, set `ROCKET_DATA_DIR=/path/to/retailrocket`.

Data load:
- `src/data/load_rocket_postgres.py`

### DE Pipeline (Airflow)
Airflow DAGs:
- `00_ingest_raw_kaggle_daily`
- `05_bootstrap_minio_daily`
- `10_build_warehouse_daily`
- `20_train_eval_publish_daily`
- `30_publish_candidates_daily`

Backfill:
- See `docs/de_backfill.md`

dbt (optional):
```bash
dbt run --profiles-dir dbt --project-dir dbt
```

Airflow variable:
- `model_version` (used by `30_publish_candidates_daily`)

---

## Full-Stack (Frontend + Spring + Model API)
### Online System Summary
This repo includes a production-ready online stack with a frontend console, Spring backend, and Python model API.

Included Components:
- Frontend: static UI in `frontend/` served by Caddy
- Backend: Spring Boot in `backend/` (recommendations, feedback, admin, health)
- Model API: FastAPI in `model-api/`
- Infra: Postgres + Redis + Caddy reverse proxy (TLS) via `docker-compose.prod.yml`

### How to Run (Production Compose)
```bash
docker-compose -f docker-compose.prod.yml up -d
```
Open in browser:
- `https://localhost` (frontend)

Key routes:
- `https://localhost/api/*` (Spring API)
- `https://localhost/model/*` (Model API)
- `https://localhost/actuator/*` (Spring Actuator)

### How to Run (Local Dev)
Model API:
```bash
python -m venv .venv_model_api
source .venv_model_api/bin/activate
pip install -r model-api/requirements.txt
uvicorn model-api.app.main:app --reload --port 8000
```
Backend:
```bash
mvn -f backend/pom.xml spring-boot:run
```

### API Contract Draft (Frontend + Spring + Python)
This section captures a field-level API contract draft for an online system.

#### 1) Frontend -> Spring: Get Recommendations
Endpoint:
- `GET /api/recommendations`

Query parameters:
- `userId` (string, required, 1-64, regex `^[a-zA-Z0-9_-]+$`)
- `scene` (string, required, enum `home|detail|cart|profile|search`)
- `size` (int, optional, default 10, range 1-50)
- `requestId` (string, optional, format `req_yyyyMMdd_HHmmss_####`; server generates if absent)

Headers:
- `x-trace-id` (string, optional)

Response 200:
```json
{
  "requestId": "req_20260128_0001",
  "userId": "u123",
  "scene": "home",
  "modelVersion": "v2026.01",
  "items": [
    {
      "itemId": "p001",
      "score": 0.92,
      "reason": "recently viewed similar items",
      "rank": 1
    }
  ],
  "ttlSeconds": 300
}
```

Response fields:
- `requestId` (string, required)
- `userId` (string, required)
- `scene` (string, required)
- `modelVersion` (string, required, format `vYYYY.MM` or `vYYYYMMDD`)
- `items` (array, required, length <= size)
  - `items[].itemId` (string, required)
  - `items[].score` (number, required, range 0-1)
  - `items[].reason` (string, optional, max 50)
  - `items[].rank` (int, required, 1..N)
- `ttlSeconds` (int, optional, default 300, range 60-600)

#### 2) Frontend -> Spring: Feedback Loop
Endpoint:
- `POST /api/feedback`

Request body:
```json
{
  "requestId": "req_20260128_0001",
  "userId": "u123",
  "itemId": "p001",
  "eventType": "click",
  "scene": "home",
  "modelVersion": "v2026.01",
  "ts": 1738022400000
}
```

Field validation:
- `requestId` (string, required)
- `userId` (string, required)
- `itemId` (string, required)
- `eventType` (string, required, enum `exposure|click|cart|purchase|dislike`)
- `scene` (string, required, enum `home|detail|cart|profile|search`)
- `modelVersion` (string, optional; if missing, backfill from requestId)
- `ts` (long, required, Unix ms timestamp)
- `extra` (object, optional; e.g., `position`, `page`, `device`)

#### 3) Spring -> Python: Model Inference
Endpoint:
- `POST /model/recommend`

Request body:
```json
{
  "requestId": "req_20260128_0001",
  "userId": "u123",
  "scene": "home",
  "numItems": 10,
  "candidateItems": ["p001", "p002", "p003"],
  "context": {
    "device": "web",
    "geo": "CN",
    "timeBucket": "night"
  }
}
```

Field validation:
- `requestId` (string, required)
- `userId` (string, required)
- `scene` (string, required)
- `numItems` (int, required, range 1-50)
- `candidateItems` (array, optional, length 1-2000)
- `context` (object, optional; e.g., device/geo/timeBucket)

Response 200:
```json
{
  "requestId": "req_20260128_0001",
  "modelVersion": "v2026.01",
  "scores": [
    { "itemId": "p001", "score": 0.92 },
    { "itemId": "p003", "score": 0.88 }
  ]
}
```

Response fields:
- `requestId` (string, required)
- `modelVersion` (string, required)
- `scores` (array, required)
  - `scores[].itemId` (string, required)
  - `scores[].score` (number, required, range 0-1)

#### 4) Common Error Shape
```json
{
  "requestId": "req_20260128_0001",
  "code": "MODEL_TIMEOUT",
  "message": "model service timeout"
}
```

Error fields:
- `requestId` (string, required)
- `code` (string, required, enum `PARAM_INVALID|MODEL_TIMEOUT|NO_CANDIDATES`)
- `message` (string, required, max 200)

### Latest Integration Test (January 29, 2026)
All endpoints passed over HTTPS behind Caddy:
- `/api/health` -> ok
- `/actuator/health` -> UP
- `/model/health` -> ok
- `/api/admin/candidates` -> 204
- `/api/recommendations` -> returns seeded candidates
- `/api/feedback` -> 204
- `/api/admin/feedback` -> returns new event
