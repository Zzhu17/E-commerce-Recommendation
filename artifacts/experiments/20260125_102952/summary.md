# Experiment Summary

Run: 20260125_102952

## Overall comparisons
- Popularity Hit@K higher in 100.0% of configs
- User_CF NDCG@K higher in 0.0% of configs
- User_CF Coverage higher in 100.0% of configs
- User_CF Diversity higher in 88.9% of configs

## Stability
- Mean delta Hit@K (user_cf - popularity): -0.2183
- Std delta Hit@K: 0.1110
- Mean delta NDCG@K (user_cf - popularity): -0.0755
- Std delta NDCG@K: 0.0389

## Sensitivity (candidate size)
model           hybrid_rule  popularity  time_decay_popularity   user_cf
candidate_size                                                          
1000               0.038556    0.011667               0.011667  0.033444
2000               0.021333    0.005833               0.005833  0.019500
5000               0.013011    0.003511               0.003511  0.010089

model           hybrid_rule  popularity  time_decay_popularity  user_cf
candidate_size                                                         
1000               0.106300    0.299811               0.299811      0.0
2000               0.057033    0.207089               0.203911      0.0
5000               0.027844    0.148111               0.148111      0.0

## Recommendation
- If popularity keeps winning Hit@K, consider hybrid ranking or add richer signals.
- If user_cf increases coverage/diversity, use it for exploration or long-tail discovery.
