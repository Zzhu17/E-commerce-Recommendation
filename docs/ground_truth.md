# Ground Truth & Event Weighting

## Ground Truth Definition
We define ground truth as the set of items a user interacted with in the **holdout window**
after a temporal split. Interactions include:
- view
- addtocart
- transaction

Each user has a set of relevant items from the test window, which is used to compute Hit@K and NDCG@K.

## Leakage Guardrails
- Negative sampling is restricted to items **not interacted within the training window** for each user.
- Test window interactions are **never** used in training or negative sampling.

## Cold-start Policy
- New users (not seen in train window) fall back to popularity-based recommendations.
- New items (not seen in train window) are excluded from candidate pools in offline evaluation.

## Event Weighting
For offline evaluation in this project, all interaction types are treated as **implicit positive feedback** (weight = 1).

If you want a stronger business signal, you can apply weighted relevance:
- transaction: 3
- addtocart: 2
- view: 1

This would prioritize purchase intent in ranking metrics such as NDCG@K.
