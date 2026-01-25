import argparse
import os
from pathlib import Path
import sys

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.data.split import temporal_split
from src.pipelines.offline_eval import load_interactions, build_y_true
from src.evaluation.metrics import hit_at_k, ndcg_at_k
from src.recommenders.popularity import fit_popularity, recommend_popularity
from src.recommenders.time_decay_popularity import fit_time_decay_popularity
from src.recommenders.user_cf import build_matrix, recommend_user_cf

OUTPUT_PATH = REPO_ROOT / "artifacts" / "experiments" / "interleaving_results.csv"


def interleave(a, b, k):
    out = []
    seen = set()
    for i in range(k):
        if i < len(a) and a[i] not in seen:
            out.append(a[i])
            seen.add(a[i])
        if i < len(b) and b[i] not in seen:
            out.append(b[i])
            seen.add(b[i])
        if len(out) >= k:
            break
    return out[:k]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL"))
    parser.add_argument("--sample-mod", type=int, default=200)
    parser.add_argument("--candidate-size", type=int, default=2000)
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-end", default="2015-06-01")
    parser.add_argument("--val-end", default="2015-06-15")
    args = parser.parse_args()

    if not args.database_url:
        raise SystemExit("DATABASE_URL not set. Use --database-url or export DATABASE_URL.")

    os.environ["DATABASE_URL"] = args.database_url

    df = load_interactions(args.sample_mod, args.val_end)
    train_df, test_df = temporal_split(df, args.train_end, args.val_end)
    train_df = train_df[["user_id", "product_id", "event_ts"]].dropna()
    test_df = test_df[["user_id", "product_id"]].dropna()

    top_items = train_df["product_id"].value_counts().head(args.candidate_size).index.tolist()
    train_df = train_df[train_df["product_id"].isin(top_items)].copy()
    test_df = test_df[test_df["product_id"].isin(top_items)].copy()

    y_true = build_y_true(test_df)
    users = sorted(set(train_df["user_id"]).intersection(y_true.keys()))
    train_df = train_df[train_df["user_id"].isin(users)].copy()
    y_true = {u: y_true[u] for u in users}

    pop_ranked = fit_popularity(train_df, top_items)
    pop_recs = recommend_popularity(users, pop_ranked, args.k)

    td_ranked = fit_time_decay_popularity(train_df, top_items, train_end=args.train_end, half_life_days=14)
    td_recs = recommend_popularity(users, td_ranked, args.k)

    matrix, user_index, item_index = build_matrix(train_df, users, top_items)
    cf_recs = recommend_user_cf(matrix, users, user_index, item_index, args.k, top_neighbors=50)

    counts = train_df.groupby("user_id")["product_id"].count()
    segments = {}
    for user_id, cnt in counts.items():
        if cnt <= 2:
            segments[user_id] = "cold"
        elif cnt <= 10:
            segments[user_id] = "light"
        else:
            segments[user_id] = "heavy"

    hybrid_recs = {}
    for user_id in users:
        seg = segments.get(user_id, "cold")
        if seg == "cold":
            hybrid_recs[user_id] = pop_recs.get(user_id, [])
        elif seg == "light":
            hybrid_recs[user_id] = td_recs.get(user_id, [])
        else:
            hybrid_recs[user_id] = cf_recs.get(user_id, [])

    interleaved = {}
    for user_id in users:
        interleaved[user_id] = interleave(pop_recs.get(user_id, []), hybrid_recs.get(user_id, []), args.k)

    rows = []
    for name, recs in [
        ("popularity", pop_recs),
        ("time_decay_popularity", td_recs),
        ("user_cf", cf_recs),
        ("hybrid_rule", hybrid_recs),
        ("interleaved_pop_hybrid", interleaved),
    ]:
        rows.append(
            {
                "model": name,
                "hit_at_k": round(hit_at_k(y_true, recs, args.k), 4),
                "ndcg_at_k": round(ndcg_at_k(y_true, recs, args.k), 4),
            }
        )

    out_df = pd.DataFrame(rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote interleaving results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
