import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg2
from sklearn.metrics.pairwise import cosine_similarity

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_CSV = REPO_ROOT / "output" / "recommendation_metrics.csv"
OUTPUT_MD = REPO_ROOT / "docs" / "recommendation_results.md"

TOP_N_ITEMS = 2000
TOP_K = 10
DEFAULT_MOD = 1000


def load_interactions(mod_value: int) -> pd.DataFrame:
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/rocket")
    sql = f"""
        SELECT user_id, product_id, event_ts
        FROM analytics.fact_events
        WHERE event_type IN ('view', 'addtocart', 'transaction')
          AND user_id % {int(mod_value)} = 0
        ORDER BY user_id, event_ts
    """
    with psycopg2.connect(db_url) as conn:
        return pd.read_sql_query(sql, conn)


def load_categories(item_ids: list) -> dict:
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/rocket")
    items_csv = ",".join(str(int(item_id)) for item_id in item_ids)
    sql = f"""
        SELECT product_id, category_id
        FROM analytics.dim_product
        WHERE product_id IN ({items_csv})
    """
    with psycopg2.connect(db_url) as conn:
        df = pd.read_sql_query(sql, conn)
    return dict(zip(df["product_id"], df["category_id"]))


def build_train_test(df: pd.DataFrame):
    user_items = df.groupby("user_id")["product_id"].apply(list)
    train_rows = []
    test_items = {}

    for user_id, items in user_items.items():
        if len(items) < 2:
            continue
        test_item = items[-1]
        train_set = {item for item in items[:-1] if item != test_item}
        if not train_set:
            continue
        test_items[user_id] = test_item
        for item in train_set:
            train_rows.append((user_id, item))

    train_df = pd.DataFrame(train_rows, columns=["user_id", "product_id"])
    return train_df, test_items


def filter_top_items(train_df: pd.DataFrame, test_items: dict, top_n: int):
    top_items = train_df["product_id"].value_counts().head(top_n).index.to_list()
    train_df = train_df[train_df["product_id"].isin(top_items)].copy()
    test_items = {u: i for u, i in test_items.items() if i in top_items}
    return train_df, test_items, top_items


def build_matrix(train_df: pd.DataFrame, users: list, items: list):
    user_index = {u: idx for idx, u in enumerate(users)}
    item_index = {i: idx for idx, i in enumerate(items)}

    matrix = np.zeros((len(users), len(items)), dtype=np.float32)
    for _, row in train_df.iterrows():
        matrix[user_index[row.user_id], item_index[row.product_id]] = 1.0
    return matrix, user_index, item_index


def recommend_user_cf(matrix: np.ndarray, user_idx: int, k: int):
    sim = cosine_similarity(matrix)
    scores = sim[user_idx].dot(matrix)
    scores[matrix[user_idx] > 0] = -np.inf
    top_k = np.argpartition(scores, -k)[-k:]
    return top_k[np.argsort(scores[top_k])[::-1]]


def recommend_popularity(pop_items_idx: list, k: int):
    return pop_items_idx[:k]


def evaluate(recs: dict, test_items: dict, item_ids: list, item_to_category: dict, k: int):
    hits = 0
    all_recommended = set()
    diversities = []

    item_idx_to_id = {idx: item_id for idx, item_id in enumerate(item_ids)}

    for user_id, rec_indices in recs.items():
        test_item = test_items.get(user_id)
        if test_item is None:
            continue
        rec_item_ids = [item_idx_to_id[idx] for idx in rec_indices]
        all_recommended.update(rec_item_ids)
        if test_item in rec_item_ids:
            hits += 1
        categories = [item_to_category.get(item_id, "unknown") for item_id in rec_item_ids]
        diversities.append(len(set(categories)) / k)

    users_eval = len(recs)
    hit_at_k = hits / users_eval if users_eval else 0.0
    coverage = len(all_recommended) / len(item_ids) if item_ids else 0.0
    diversity = float(np.mean(diversities)) if diversities else 0.0

    return {
        "hit_at_k": round(hit_at_k, 4),
        "coverage": round(coverage, 4),
        "diversity": round(diversity, 4),
        "users_eval": users_eval,
        "items_eval": len(item_ids),
    }


def main():
    mod_value = int(os.getenv("RECO_SAMPLE_MOD", DEFAULT_MOD))

    df = load_interactions(mod_value)
    if df.empty:
        raise RuntimeError("No interactions loaded. Check DATABASE_URL or sampling filter.")

    train_df, test_items = build_train_test(df)
    train_df, test_items, item_ids = filter_top_items(train_df, test_items, TOP_N_ITEMS)

    users = sorted(test_items.keys())
    train_df = train_df[train_df["user_id"].isin(users)].copy()

    matrix, user_index, item_index = build_matrix(train_df, users, item_ids)
    item_to_category = load_categories(item_ids)

    popularity = train_df["product_id"].value_counts().index.tolist()
    pop_idx = [item_index[item] for item in popularity if item in item_index]

    baseline_recs = {
        user_id: recommend_popularity(pop_idx, TOP_K)
        for user_id in users
    }

    model_recs = {
        user_id: recommend_user_cf(matrix, user_index[user_id], TOP_K)
        for user_id in users
    }

    baseline_metrics = evaluate(baseline_recs, test_items, item_ids, item_to_category, TOP_K)
    model_metrics = evaluate(model_recs, test_items, item_ids, item_to_category, TOP_K)

    output_df = pd.DataFrame(
        [
            {"model": "popularity", **baseline_metrics, "k": TOP_K},
            {"model": "user_cf", **model_metrics, "k": TOP_K},
        ]
    )

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(OUTPUT_CSV, index=False)

    md_lines = [
        "# Recommendation Results (Offline)",
        "",
        f"Sample filter: user_id % {mod_value} == 0",
        f"Top items considered: {TOP_N_ITEMS}",
        f"K: {TOP_K}",
        "",
        output_df.to_markdown(index=False),
    ]
    OUTPUT_MD.write_text("\n".join(md_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
