# E-Commerce Recommendation (Offline Evaluation)

Status:
- Offline recommendation evaluation complete
- Baseline vs model comparison implemented
- Metrics focus on business-aligned proxy indicators

## Business Objective
This project evaluates an e-commerce product recommendation strategy in an offline setting.

The recommendation system is designed to:
- Improve product discovery
- Increase user engagement
- Support downstream business metrics such as click-through rate and conversion rate

Given data constraints, the focus is on pre-deployment evaluation rather than online experimentation.

## Scope & Constraints
This project focuses on offline recommendation evaluation due to the absence of real-time user
interaction signals such as impressions, clicks, or purchases after recommendation exposure.

As a result:
- Online A/B testing is not performed
- Model performance is evaluated using offline proxy metrics
- Results are interpreted as potential uplift rather than guaranteed production impact

This reflects a common early-stage evaluation process in real-world recommendation systems.

## Data Description
- User-item interactions derived from historical events in RetailRocket
- Implicit feedback assumption: past interactions indicate relevance
- No negative feedback is explicitly observed
- Evaluation uses a temporal split to reduce information leakage

## Recommendation Approaches
### Baseline: Popularity-Based Recommendation
- Items ranked by overall interaction frequency
- Same recommendation list for all users
- Serves as a simple, interpretable benchmark

### Baseline: Time-Decayed Popularity
- Items ranked by recency-weighted interaction frequency
- Prioritizes recent trends over older interactions

### Model: Collaborative Filtering (User-Based)
- Learns user-item interaction patterns
- Produces personalized recommendation lists
- Captures latent preferences beyond popularity bias

### Hybrid Decision Rule (Segmented)
- cold users -> popularity
- light users -> time-decayed popularity
- heavy users -> user_cf

## Evaluation Metrics (Offline Proxies)
Given the offline setting, the following metrics are used as business-aligned proxies:

- Hit@K: whether a relevant item appears in the top-K recommendations
- NDCG@K: rewards higher-ranked hits, closer to online ranking quality
- Coverage: proportion of unique items recommended across all users
- Diversity: average category variety within each user's top-K list

These metrics serve as proxies for online engagement, product discovery, and exploration.

## Results Summary (Sampled Offline Evaluation)
Configuration:
- Temporal split with sampled users (sample_mod in {50,100,200})
- Candidate pool in {1k,2k,5k}
- K in {5,10,20}

Robustness grid: K ∈ {5,10,20}, candidate pool ∈ {1k,2k,5k}, and 3 sampling ratios, with bootstrap CIs and stability across 81 configurations.

| Metric | Popularity Baseline | Collaborative Filtering |
| --- | --- | --- |
| Hit@K (avg) | 0.2183 | 0.0000 |
| NDCG@K (avg) | 0.0755 | 0.0000 |
| Coverage@K (avg) | 0.0070 | 0.0210 |
| Diversity@K (avg) | 0.5574 | 0.9006 |

The collaborative filtering model increases coverage and diversity, indicating broader catalog
exposure, while underperforming the popularity baseline on Hit@K and NDCG@10 in this sample.
This suggests that popularity remains a strong baseline on sparse interaction data and that
personalization may require richer signals or hybrid strategies.

Interleaving check (popularity vs hybrid) shows lower NDCG@10 for the interleaved list
(0.0334) than popularity (0.0944) in the current sample, indicating hybrid needs stronger
personalization signals before deployment.

Single-run sanity check (seed=42, sample_mod=200, candidate_size=2000, K=10):
- NDCG@10: popularity 0.0944, collaborative filtering 0.0000

## Trade-offs & Observations
- Better coverage/diversity can come at the cost of lower Hit@K
- This highlights the balance between recommendation accuracy and exploration
- In production systems, hybrid ranking or exploration-aware strategies are often used

## Limitations & Next Steps
- Offline metrics do not guarantee online performance
- No user feedback loop is available
- Future work may include:
  - Online A/B testing
  - Exploration strategies (epsilon-greedy, Thompson sampling)
  - Hybrid recommendation approaches

## Reproducibility
Data load:
- `src/data/load_rocket_postgres.py`
- Legacy MySQL loader (deprecated): `legacy/load_data_to_mysql.py`

Offline evaluation:
```bash
export DATABASE_URL="postgresql://rocket:Zzp990812@localhost:5434/rocket"
RECO_SAMPLE_MOD=200 python src/models/evaluate_recommender_offline.py
```

Outputs:
- `output/recommendation_metrics.csv`
- `docs/recommendation_results.md`
- `ecommerce-recommend.pdf` (Power BI dashboard screenshots)
- `docs/ground_truth.md`
- `artifacts/data_fingerprint.json`
- `artifacts/experiments/interleaving_results.csv`
- `artifacts/experiments/20260125_102952/` (latest grid run artifacts)

## Experiment Framework (DS)
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

Step 2 diagnostics and hypotheses:
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
python experiments/interleaving_eval.py
```


## Step 2 (Evaluation Upgrade)
- Added ranking quality metric: NDCG@K
- Added user segmentation: cold (1-2), light (3-10), heavy (11+)
- Added diagnostics: sparsity + long-tail plots
- Added online hypotheses for A/B validation

Run diagnostics:
```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/rocket"
python experiments/data_diagnostics.py
```
