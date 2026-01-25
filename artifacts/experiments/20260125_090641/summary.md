# Experiment Summary

Run: 20260125_090641

## Overall comparisons
- Popularity Hit@K higher in 100.0% of configs
- User_CF NDCG@K higher in 0.0% of configs
- User_CF Coverage higher in 100.0% of configs
- User_CF Diversity higher in 100.0% of configs

## Stability
- Mean delta Hit@K (user_cf - popularity): -0.2928
- Std delta Hit@K: 0.1034
- Mean delta NDCG@K (user_cf - popularity): -0.0897
- Std delta NDCG@K: 0.0397

## Sensitivity (candidate size)
model           hybrid_rule  popularity  time_decay_popularity   user_cf
candidate_size                                                          
1000               0.031667    0.011667               0.011667  0.020333
2000               0.017000    0.005833               0.005833  0.011167
5000               0.015067    0.005333               0.005333  0.009433

model           hybrid_rule  popularity  time_decay_popularity  user_cf
candidate_size                                                         
1000               0.083333    0.375000               0.375000      0.0
2000               0.060600    0.272700               0.272700      0.0
5000               0.025633    0.230767               0.230767      0.0

## Recommendation
- If popularity keeps winning Hit@K, consider hybrid ranking or add richer signals.
- If user_cf increases coverage/diversity, use it for exploration or long-tail discovery.
