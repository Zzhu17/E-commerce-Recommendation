# Online Hypotheses (Post-Offline Evaluation)

H1 (Heavy users): In the heavy segment, the collaborative filtering model achieves higher NDCG@10 than the popularity baseline. Therefore, in an online A/B test, we expect higher CTR for heavy users under the CF variant.

H2 (Overall): The CF model increases coverage and diversity compared to popularity, so we expect higher long-tail exposure at the cost of a potential short-term CTR drop.

Primary metric:
- CTR (click-through rate)

Guardrails:
- Recommendation latency
- Null recommendation rate
- Long-tail exposure share
