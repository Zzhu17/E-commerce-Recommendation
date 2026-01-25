from typing import List

import pandas as pd


def fit_time_decay_popularity(
    train_df: pd.DataFrame,
    candidate_items: List[int],
    train_end: str,
    half_life_days: int = 14,
) -> List[int]:
    df = train_df.copy()
    df["event_ts"] = pd.to_datetime(df["event_ts"])
    train_end_ts = pd.to_datetime(train_end)
    age_days = (train_end_ts - df["event_ts"]).dt.days.clip(lower=0)
    weights = 0.5 ** (age_days / max(half_life_days, 1))
    df["weight"] = weights

    scored = (
        df.groupby("product_id")["weight"]
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )
    ranked = [item for item in scored if item in candidate_items]
    return ranked
