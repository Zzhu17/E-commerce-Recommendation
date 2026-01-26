import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg2

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.data.split import temporal_split
from src.data.graph import build_mappings, build_train_edges_weighted


def hash_frame(df: pd.DataFrame) -> str:
    m = hashlib.sha256()
    for _, row in df.iterrows():
        m.update(f"{row.user_id}|{row.product_id}|{row.event_ts}|{row.event_type}".encode())
    return m.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ds", required=True)
    parser.add_argument("--train-end", default="2015-06-01")
    parser.add_argument("--val-end", default="2015-06-15")
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket"))
    args = parser.parse_args()

    conn = psycopg2.connect(args.database_url)
    conn.autocommit = False
    try:
        df = pd.read_sql_query(
            """
            SELECT user_id, item_id AS product_id, event_ts, event_type,
                   CASE event_type WHEN 'transaction' THEN 3 WHEN 'addtocart' THEN 2 ELSE 1 END AS event_weight
            FROM stg.events
            """,
            conn,
        )
        train_df, test_df = temporal_split(df, args.train_end, args.val_end)
        users = sorted(train_df["user_id"].unique().tolist())
        items = sorted(train_df["product_id"].unique().tolist())
        mapping = build_mappings(users, items)
        edges = build_train_edges_weighted(train_df, mapping)

        snapshot_id = f"snap_{args.ds}_{datetime.utcnow().strftime('%H%M%S')}"
        data_hash = hash_frame(train_df[["user_id", "product_id", "event_ts", "event_type"]])

        with conn.cursor() as cur:
            cur.execute(Path("sql/feature/25_feature_tables.sql").read_text())
            cur.execute(
                """
                INSERT INTO feat.feature_snapshots (snapshot_id, ds, train_range, test_range, logic_version, data_hash, counts_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    snapshot_id,
                    args.ds,
                    args.train_end,
                    args.val_end,
                    os.getenv("GIT_COMMIT", "unknown"),
                    data_hash,
                    json.dumps({
                        "n_users": len(users),
                        "n_items": len(items),
                        "n_edges": int(len(edges)),
                    }),
                ),
            )

            mapping_rows = []
            for user_id, u_idx in mapping.user2idx.items():
                mapping_rows.append((snapshot_id, user_id, u_idx, None, None))
            for item_id, i_idx in mapping.item2idx.items():
                mapping_rows.append((snapshot_id, None, None, item_id, i_idx))
            cur.executemany(
                "INSERT INTO feat.id_mappings (snapshot_id, user_id, user_idx, item_id, item_idx) VALUES (%s,%s,%s,%s,%s)",
                mapping_rows,
            )

            edge_rows = [(snapshot_id, int(u), int(i), float(w)) for u, i, w in edges]
            cur.executemany(
                "INSERT INTO feat.train_edges (snapshot_id, user_idx, item_idx, weight) VALUES (%s,%s,%s,%s)",
                edge_rows,
            )

            holdout_rows = []
            for _, row in test_df.iterrows():
                u_idx = mapping.user2idx.get(row.user_id)
                i_idx = mapping.item2idx.get(row.product_id)
                if u_idx is None or i_idx is None:
                    continue
                holdout_rows.append((snapshot_id, u_idx, i_idx))
            cur.executemany(
                "INSERT INTO feat.holdout_truth (snapshot_id, user_idx, item_idx) VALUES (%s,%s,%s)",
                holdout_rows,
            )

        conn.commit()
        print(snapshot_id)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
