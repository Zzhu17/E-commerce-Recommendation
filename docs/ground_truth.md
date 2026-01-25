# Ground Truth & Event Weighting

## Ground Truth Definition
We define ground truth as the set of items a user interacted with in the **holdout window**
after a temporal split. Interactions include:
- view
- addtocart
- transaction

Each user has a set of relevant items from the test window, which is used to compute Hit@K and NDCG@K.

## Event Weighting
For offline evaluation in this project, all interaction types are treated as **implicit positive feedback** (weight = 1).

If you want a stronger business signal, you can apply weighted relevance:
- transaction: 3
- addtocart: 2
- view: 1

This would prioritize purchase intent in ranking metrics such as NDCG@K.
