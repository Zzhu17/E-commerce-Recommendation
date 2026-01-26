from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


@dataclass
class GraphMapping:
    user2idx: Dict[int, int]
    item2idx: Dict[int, int]
    idx2user: Dict[int, int]
    idx2item: Dict[int, int]


def build_mappings(users: List[int], items: List[int]) -> GraphMapping:
    user2idx = {user_id: idx for idx, user_id in enumerate(users)}
    item2idx = {item_id: idx for idx, item_id in enumerate(items)}
    idx2user = {idx: user_id for user_id, idx in user2idx.items()}
    idx2item = {idx: item_id for item_id, idx in item2idx.items()}
    return GraphMapping(user2idx=user2idx, item2idx=item2idx, idx2user=idx2user, idx2item=idx2item)


def build_train_edges(train_df: pd.DataFrame, mapping: GraphMapping) -> np.ndarray:
    user_idx = train_df["user_id"].map(mapping.user2idx)
    item_idx = train_df["product_id"].map(mapping.item2idx)
    edges = pd.DataFrame({"u_idx": user_idx, "i_idx": item_idx}).dropna()
    return edges.astype({"u_idx": int, "i_idx": int}).to_numpy()


def build_train_edges_weighted(train_df: pd.DataFrame, mapping: GraphMapping) -> np.ndarray:
    if "event_weight" not in train_df.columns:
        raise ValueError("event_weight column not found for weighted edges.")
    user_idx = train_df["user_id"].map(mapping.user2idx)
    item_idx = train_df["product_id"].map(mapping.item2idx)
    weights = train_df["event_weight"]
    edges = pd.DataFrame({"u_idx": user_idx, "i_idx": item_idx, "weight": weights}).dropna()
    return edges.astype({"u_idx": int, "i_idx": int, "weight": float}).to_numpy()


def build_user_pos(edges: np.ndarray) -> Dict[int, set]:
    user_pos: Dict[int, set] = {}
    for u_idx, i_idx in edges:
        user_pos.setdefault(int(u_idx), set()).add(int(i_idx))
    return user_pos
