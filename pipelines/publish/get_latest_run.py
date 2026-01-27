import argparse
import os

import psycopg2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", default="lightgcn")
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket"))
    args = parser.parse_args()

    conn = psycopg2.connect(args.database_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT run_id
                FROM ml.runs
                WHERE model_name = %s AND status = 'finished'
                ORDER BY finished_at DESC NULLS LAST
                LIMIT 1
                """,
                (args.model_name,),
            )
            row = cur.fetchone()
            if not row:
                raise RuntimeError("No finished runs found")
            print(row[0])
    finally:
        conn.close()


if __name__ == "__main__":
    main()
