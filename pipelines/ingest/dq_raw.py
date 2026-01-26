import argparse
import os

import psycopg2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket"))
    args = parser.parse_args()

    conn = psycopg2.connect(args.database_url)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM raw.events_raw WHERE batch_id = %s", (args.batch_id,))
            events = cur.fetchone()[0]
            if events == 0:
                raise RuntimeError("DQ failed: raw.events_raw is empty")
            cur.execute(
                "SELECT COUNT(*) FROM raw.events_raw WHERE batch_id = %s AND event_type IS NULL",
                (args.batch_id,),
            )
            null_types = cur.fetchone()[0]
            if null_types > 0:
                raise RuntimeError("DQ failed: raw.events_raw has null event_type")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
