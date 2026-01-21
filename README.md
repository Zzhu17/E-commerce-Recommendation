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

### Model: Collaborative Filtering (User-Based)
- Learns user-item interaction patterns
- Produces personalized recommendation lists
- Captures latent preferences beyond popularity bias

## Evaluation Metrics (Offline Proxies)
Given the offline setting, the following metrics are used as business-aligned proxies:

- Hit@K: whether a relevant item appears in the top-K recommendations
- Coverage: proportion of unique items recommended across all users
- Diversity: average category variety within each user's top-K list

These metrics serve as proxies for online engagement, product discovery, and exploration.

## Results Summary (Sampled Offline Evaluation)
Configuration:
- Sample filter: user_id % 200 == 0
- Top items considered: 2000
- K = 10

| Metric | Popularity Baseline | Collaborative Filtering |
| --- | --- | --- |
| Hit@10 | 0.0185 | 0.0093 |
| Coverage | 0.0050 | 0.0275 |
| Diversity | 0.8000 | 0.8843 |

The collaborative filtering model increases coverage and diversity, indicating broader catalog
exposure, while underperforming the popularity baseline on Hit@K in this sample. This suggests
that popularity remains a strong baseline on sparse interaction data and that personalization
may require richer signals or hybrid strategies.

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

Offline evaluation:
```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/rocket"
RECO_SAMPLE_MOD=200 python src/models/evaluate_recommender_offline.py
```

Outputs:
- `output/recommendation_metrics.csv`
- `docs/recommendation_results.md`
