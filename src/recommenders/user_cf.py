from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def build_matrix(train_df: pd.DataFrame, users: List[int], items: List[int]) -> Tuple[np.ndarray, dict, dict]:
    user_index = {u: idx for idx, u in enumerate(users)}
    item_index = {i: idx for idx, i in enumerate(items)}
    matrix = np.zeros((len(users), len(items)), dtype=np.float32)

    for _, row in train_df.iterrows():
        u_idx = user_index.get(row.user_id)
        i_idx = item_index.get(row.product_id)
        if u_idx is None or i_idx is None:
            continue
        matrix[u_idx, i_idx] = 1.0

    return matrix, user_index, item_index


def recommend_user_cf(
    matrix: np.ndarray,
    users: List[int],
    user_index: dict,
    item_index: dict,
    k: int,
    top_neighbors: int = 50,
) -> Dict[int, List[int]]:
    sim = cosine_similarity(matrix)
    recommendations = {}
    item_ids = list(item_index.keys())
    idx_to_item = {idx: item_id for item_id, idx in item_index.items()}

    for user_id in users:
        u_idx = user_index[user_id]
        scores = sim[u_idx].dot(matrix)
        scores[matrix[u_idx] > 0] = -np.inf

        if top_neighbors and top_neighbors < sim.shape[0]:
            neighbor_idx = np.argpartition(sim[u_idx], -top_neighbors)[-top_neighbors:]
            scores = sim[u_idx, neighbor_idx].dot(matrix[neighbor_idx])
            scores[matrix[u_idx] > 0] = -np.inf

        top_k = np.argpartition(scores, -k)[-k:]
        top_k = top_k[np.argsort(scores[top_k])[::-1]]
        recommendations[user_id] = [idx_to_item[idx] for idx in top_k if idx in idx_to_item]

    return recommendations
