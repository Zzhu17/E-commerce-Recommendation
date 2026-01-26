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

from src.evaluation.metrics import hit_at_k, ndcg_at_k, coverage_at_k, diversity_at_k


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--snapshot-id", required=True)
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket"))
    parser.add_argument("--k", type=int, default=10)
    args = parser.parse_args()

    conn = psycopg2.connect(args.database_url)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_idx, item_idx FROM feat.holdout_truth WHERE snapshot_id = %s", (args.snapshot_id,))
            truth = cur.fetchall()
            cur.execute("SELECT user_idx, item_idx FROM feat.train_edges WHERE snapshot_id = %s", (args.snapshot_id,))
            edges = cur.fetchall()

        y_true = {}
        for u, i in truth:
            y_true.setdefault(int(u), set()).add(int(i))

        items = sorted({int(i) for _, i in edges})
        pop_counts = {}
        for _, i in edges:
            pop_counts[int(i)] = pop_counts.get(int(i), 0) + 1
        ranked = [i for i, _ in sorted(pop_counts.items(), key=lambda x: x[1], reverse=True)]
        recs = {u: ranked[: args.k] for u in y_true.keys()}

        hit = hit_at_k(y_true, recs, args.k)
        ndcg = ndcg_at_k(y_true, recs, args.k)
        coverage = coverage_at_k(recs, items, args.k)
        diversity = diversity_at_k(recs, {}, args.k)

        with conn.cursor() as cur:
            cur.execute(Path("sql/ml/30_ml_tables.sql").read_text())
            cur.execute(
                "INSERT INTO ml.metrics (run_id, segment, k, hit, ndcg, coverage, diversity, ci_json) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (args.run_id, "all", args.k, hit, ndcg, coverage, diversity, json.dumps({})),
            )
        conn.commit()
        print("metrics written")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
