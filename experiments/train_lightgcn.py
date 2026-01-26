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
from src.data.graph import build_mappings, build_train_edges, build_user_pos
from src.recommenders.lightgcn import LightGCNConfig, train_lightgcn

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "models" / "lightgcn"


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
    parser.add_argument("--dim", type=int, default=64)
    parser.add_argument("--num-layers", type=int, default=3)
    parser.add_argument("--num-neg", type=int, default=1)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--batch-size", type=int, default=2048)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--reg", type=float, default=1e-4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--eval-k", type=int, default=10)
    parser.add_argument("--eval-every", type=int, default=5)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--score-batch", type=int, default=512)
    parser.add_argument("--run-id", default=None)
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
    user_pos = build_user_pos(edges)

    val_y_true = {}
    for _, row in test_df.iterrows():
        u_idx = mapping.user2idx.get(row.user_id)
        i_idx = mapping.item2idx.get(row.product_id)
        if u_idx is None or i_idx is None:
            continue
        val_y_true.setdefault(u_idx, set()).add(i_idx)

    cfg = LightGCNConfig(
        embedding_dim=args.dim,
        num_layers=args.num_layers,
        lr=args.lr,
        batch_size=args.batch_size,
        num_neg=args.num_neg,
        epochs=args.epochs,
        reg=args.reg,
        seed=args.seed,
        eval_k=args.eval_k,
        eval_every=args.eval_every,
        patience=args.patience,
        score_batch=args.score_batch,
    )

    user_emb, item_emb, metrics = train_lightgcn(
        edges,
        user_pos,
        len(users),
        len(items),
        cfg,
        val_y_true=val_y_true,
    )

    run_id = args.run_id or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_dir = ARTIFACTS_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    np.save(out_dir / "user_emb.npy", user_emb)
    np.save(out_dir / "item_emb.npy", item_emb)
    (out_dir / "config.yaml").write_text(yaml.safe_dump(cfg.__dict__), encoding="utf-8")
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Saved LightGCN artifacts to {out_dir}")


if __name__ == "__main__":
    main()
