import argparse
import json
import os
from pathlib import Path

import pandas as pd
import psycopg2

from src.data.split import temporal_split
from src.data.graph import build_mappings, build_train_edges

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "artifacts"
MAPPINGS_DIR = ARTIFACTS_DIR / "mappings"
GRAPH_DIR = ARTIFACTS_DIR / "graph"


def load_interactions(sample_mod: int, val_end: str) -> pd.DataFrame:
    db_url = os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket")
    sql = f"""
        SELECT user_id, product_id, event_ts
        FROM analytics.fact_events
        WHERE event_type IN ('view', 'addtocart', 'transaction')
          AND user_id % {int(sample_mod)} = 0
          AND event_ts <= '{val_end}'
        ORDER BY user_id, event_ts
    """
    with psycopg2.connect(db_url) as conn:
        return pd.read_sql_query(sql, conn)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-end", default="2015-06-01")
    parser.add_argument("--val-end", default="2015-06-15")
    parser.add_argument("--sample-mod", type=int, default=200)
    args = parser.parse_args()

    df = load_interactions(args.sample_mod, args.val_end)
    if df.empty:
        raise RuntimeError("No interactions loaded. Check DATABASE_URL or sampling filter.")

    train_df, test_df = temporal_split(df, args.train_end, args.val_end)
    train_df = train_df[["user_id", "product_id", "event_ts"]].dropna()
    test_df = test_df[["user_id", "product_id"]].dropna()

    users = sorted(train_df["user_id"].unique().tolist())
    items = sorted(train_df["product_id"].unique().tolist())
    mapping = build_mappings(users, items)

    edges = build_train_edges(train_df, mapping)

    MAPPINGS_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)

    (MAPPINGS_DIR / "user2idx.json").write_text(json.dumps(mapping.user2idx, indent=2), encoding="utf-8")
    (MAPPINGS_DIR / "item2idx.json").write_text(json.dumps(mapping.item2idx, indent=2), encoding="utf-8")
    (MAPPINGS_DIR / "idx2user.json").write_text(json.dumps(mapping.idx2user, indent=2), encoding="utf-8")
    (MAPPINGS_DIR / "idx2item.json").write_text(json.dumps(mapping.idx2item, indent=2), encoding="utf-8")

    edge_df = pd.DataFrame(edges, columns=["u_idx", "i_idx"])
    edge_df.to_parquet(GRAPH_DIR / "train_edges.parquet", index=False)

    stats = {
        "n_users": len(users),
        "n_items": len(items),
        "n_edges": int(len(edges)),
        "train_end": args.train_end,
        "val_end": args.val_end,
        "sample_mod": args.sample_mod,
    }
    (GRAPH_DIR / "graph_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")

    print(f"Saved mappings to {MAPPINGS_DIR}")
    print(f"Saved train edges to {GRAPH_DIR / 'train_edges.parquet'}")


if __name__ == "__main__":
    main()
