from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from scipy.sparse import csr_matrix
import implicit


@dataclass
class ALSConfig:
    factors: int = 64
    regularization: float = 0.01
    iterations: int = 30
    alpha: float = 1.0


def build_user_item_matrix(edges: np.ndarray, num_users: int, num_items: int, alpha: float = 1.0) -> csr_matrix:
    if edges.size == 0:
        raise ValueError("No edges provided for ALS.")
    data = np.ones(len(edges), dtype=np.float32) * alpha
    user_idx = edges[:, 0].astype(np.int64)
    item_idx = edges[:, 1].astype(np.int64)
    return csr_matrix((data, (user_idx, item_idx)), shape=(num_users, num_items))


def fit_als(user_items: csr_matrix, config: ALSConfig) -> implicit.als.AlternatingLeastSquares:
    model = implicit.als.AlternatingLeastSquares(
        factors=config.factors,
        regularization=config.regularization,
        iterations=config.iterations,
    )
    model.fit(user_items.T)
    return model


def recommend_als(
    model: implicit.als.AlternatingLeastSquares,
    user_items: csr_matrix,
    users: List[int],
    k: int,
) -> Dict[int, List[int]]:
    recs: Dict[int, List[int]] = {}
    for u in users:
        items, _ = model.recommend(u, user_items, N=k, filter_already_liked_items=True)
        recs[int(u)] = [int(i) for i in items]
    return recs
