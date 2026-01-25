from typing import Dict, List

import pandas as pd


def fit_popularity(train_df: pd.DataFrame, candidate_items: List[int]) -> List[int]:
    counts = train_df["product_id"].value_counts()
    ordered = [item for item in counts.index.tolist() if item in candidate_items]
    return ordered


def recommend_popularity(users: List[int], ranked_items: List[int], k: int) -> Dict[int, List[int]]:
    top_k = ranked_items[:k]
    return {user_id: top_k for user_id in users}
