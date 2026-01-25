import math
from typing import Dict, List, Set


def hit_at_k(y_true: Dict[int, Set[int]], y_pred: Dict[int, List[int]], k: int) -> float:
    hits = 0
    users = 0
    for user_id, true_items in y_true.items():
        pred_items = y_pred.get(user_id, [])[:k]
        if not pred_items:
            continue
        users += 1
        if true_items.intersection(pred_items):
            hits += 1
    return hits / users if users else 0.0


def ndcg_at_k(y_true: Dict[int, Set[int]], y_pred: Dict[int, List[int]], k: int) -> float:
    scores = []
    for user_id, true_items in y_true.items():
        pred_items = y_pred.get(user_id, [])[:k]
        if not pred_items:
            continue
        dcg = 0.0
        for rank, item_id in enumerate(pred_items):
            if item_id in true_items:
                dcg += 1.0 / math.log2(rank + 2)
        ideal_hits = min(len(true_items), k)
        if ideal_hits == 0:
            continue
        idcg = sum(1.0 / math.log2(rank + 2) for rank in range(ideal_hits))
        scores.append(dcg / idcg if idcg else 0.0)
    return sum(scores) / len(scores) if scores else 0.0


def coverage_at_k(y_pred: Dict[int, List[int]], all_items: List[int], k: int) -> float:
    if not all_items:
        return 0.0
    recommended = set()
    for items in y_pred.values():
        recommended.update(items[:k])
    return len(recommended) / len(all_items)


def diversity_at_k(
    y_pred: Dict[int, List[int]],
    item_to_category: Dict[int, int],
    k: int,
) -> float:
    diversities = []
    for items in y_pred.values():
        if not items:
            continue
        categories = [item_to_category.get(item, "unknown") for item in items[:k]]
        diversities.append(len(set(categories)) / k)
    return sum(diversities) / len(diversities) if diversities else 0.0
