import argparse
import os
from pathlib import Path

import psycopg2


def run_sql(cursor, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    cursor.execute(sql)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket"))
    args = parser.parse_args()

    conn = psycopg2.connect(args.database_url)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            run_sql(cur, Path("sql/staging/10_build_staging.sql"))
            run_sql(cur, Path("sql/marts/20_build_marts.sql"))
            conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
