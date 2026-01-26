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

from src.recommenders.als import ALSConfig, build_user_item_matrix, fit_als


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-id", required=True)
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket"))
    args = parser.parse_args()

    conn = psycopg2.connect(args.database_url)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_idx, item_idx, weight FROM feat.train_edges WHERE snapshot_id = %s", (args.snapshot_id,))
            edges = cur.fetchall()

        if not edges:
            raise RuntimeError("No edges found for snapshot")

        edges_np = np.array(edges, dtype=float)
        n_users = int(edges_np[:, 0].max()) + 1
        n_items = int(edges_np[:, 1].max()) + 1

        cfg = ALSConfig()
        user_items = build_user_item_matrix(edges_np, n_users, n_items)
        model = fit_als(user_items, cfg)

        run_id = f"als_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        out_dir = Path("artifacts") / run_id
        out_dir.mkdir(parents=True, exist_ok=True)
        np.save(out_dir / "user_factors.npy", model.user_factors)
        np.save(out_dir / "item_factors.npy", model.item_factors)

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
                    "als",
                    json.dumps(cfg.__dict__),
                    os.getenv("GIT_COMMIT", "unknown"),
                    "finished",
                    datetime.utcnow(),
                    datetime.utcnow(),
                ),
            )
            cur.execute(
                "INSERT INTO ml.artifacts (run_id, artifact_type, uri, checksum) VALUES (%s,%s,%s,%s)",
                (run_id, "factors", str(out_dir), ""),
            )
        conn.commit()
        print(run_id)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
