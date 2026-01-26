import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg2
import yaml

from src.data.split import temporal_split
from src.data.graph import build_mappings, build_train_edges
from src.recommenders.als import ALSConfig, build_user_item_matrix, fit_als

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "models" / "als"


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
    parser.add_argument("--factors", type=int, default=64)
    parser.add_argument("--reg", type=float, default=0.01)
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    df = load_interactions(args.sample_mod, args.val_end)
    if df.empty:
        raise RuntimeError("No interactions loaded. Check DATABASE_URL or sampling filter.")

    train_df, _ = temporal_split(df, args.train_end, args.val_end)
    train_df = train_df[["user_id", "product_id", "event_ts"]].dropna()

    users = sorted(train_df["user_id"].unique().tolist())
    items = sorted(train_df["product_id"].unique().tolist())
    mapping = build_mappings(users, items)
    edges = build_train_edges(train_df, mapping)

    cfg = ALSConfig(
        factors=args.factors,
        regularization=args.reg,
        iterations=args.iterations,
        alpha=args.alpha,
    )

    user_items = build_user_item_matrix(edges, len(users), len(items), alpha=args.alpha)
    model = fit_als(user_items, cfg)

    run_id = args.run_id or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_dir = ARTIFACTS_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    np.save(out_dir / "user_factors.npy", model.user_factors)
    np.save(out_dir / "item_factors.npy", model.item_factors)
    (out_dir / "config.yaml").write_text(yaml.safe_dump(cfg.__dict__), encoding="utf-8")
    (out_dir / "metrics.json").write_text(json.dumps({"status": "trained"}, indent=2), encoding="utf-8")

    print(f"Saved ALS artifacts to {out_dir}")


if __name__ == "__main__":
    main()
