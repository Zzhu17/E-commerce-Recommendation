import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import psycopg2

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.recommenders.lightgcn import LightGCNConfig, train_lightgcn, recommend_lightgcn


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-id", required=True)
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket"))
    parser.add_argument("--k", type=int, default=10)
    args = parser.parse_args()

    conn = psycopg2.connect(args.database_url)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_idx, item_idx, weight FROM feat.train_edges WHERE snapshot_id = %s", (args.snapshot_id,))
            edges = cur.fetchall()
            cur.execute("SELECT user_idx, item_idx FROM feat.holdout_truth WHERE snapshot_id = %s", (args.snapshot_id,))
            holdout = cur.fetchall()

        if not edges:
            raise RuntimeError("No edges found for snapshot")

        edges_np = np.array(edges, dtype=float)
        user_pos = {}
        for u, i, _ in edges_np:
            user_pos.setdefault(int(u), set()).add(int(i))

        val_y_true = {}
        for u, i in holdout:
            val_y_true.setdefault(int(u), set()).add(int(i))

        n_users = int(edges_np[:, 0].max()) + 1
        n_items = int(edges_np[:, 1].max()) + 1

        cfg = LightGCNConfig()
        user_emb, item_emb, metrics = train_lightgcn(edges_np, user_pos, n_users, n_items, cfg, val_y_true=val_y_true)

        run_id = f"lightgcn_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        out_dir = Path("artifacts") / run_id
        out_dir.mkdir(parents=True, exist_ok=True)
        np.save(out_dir / "user_emb.npy", user_emb)
        np.save(out_dir / "item_emb.npy", item_emb)
        (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

        # build topK
        recs = recommend_lightgcn(user_emb, item_emb, user_pos, args.k)
        rows = []
        for u_idx, items in recs.items():
            for rank, i_idx in enumerate(items, 1):
                rows.append({
                    "user_id": int(u_idx),
                    "rank": rank,
                    "item_id": int(i_idx),
                    "score": 0.0,
                })
        import pandas as pd
        pd.DataFrame(rows).to_parquet(out_dir / "user_topk.parquet", index=False)

        with conn.cursor() as cur:
            cur.execute(Path("sql/ml/30_ml_tables.sql").read_text())
            cur.execute(
                """
                INSERT INTO ml.runs (run_id, snapshot_id, model_name, config_json, git_commit, status, started_at, finished_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    run_id,
                    args.snapshot_id,
                    "lightgcn",
                    json.dumps(cfg.__dict__),
                    os.getenv("GIT_COMMIT", "unknown"),
                    "finished",
                    datetime.utcnow(),
                    datetime.utcnow(),
                ),
            )
            cur.execute(
                "INSERT INTO ml.artifacts (run_id, artifact_type, uri, checksum) VALUES (%s,%s,%s,%s)",
                (run_id, "embeddings", str(out_dir), ""),
            )
        conn.commit()
        print(run_id)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
