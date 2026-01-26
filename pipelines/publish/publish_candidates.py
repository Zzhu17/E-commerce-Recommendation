import argparse
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--topk", required=True)
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket"))
    args = parser.parse_args()

    df = pd.read_parquet(args.topk)
    df["generated_at"] = datetime.utcnow()
    df["model_version"] = args.run_id

    conn = psycopg2.connect(args.database_url)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute(Path("sql/serving/40_serving_tables.sql").read_text())
            cur.execute("DELETE FROM serving.reco_candidates WHERE model_version = %s", (args.run_id,))
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                cur.execute(
                    """
                    INSERT INTO serving.reco_candidates (model_version, user_id, rank, item_id, score, generated_at)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        row["model_version"],
                        int(row["user_id"]),
                        int(row["rank"]),
                        int(row["item_id"]),
                        float(row["score"]),
                        row["generated_at"],
                    ),
                )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
