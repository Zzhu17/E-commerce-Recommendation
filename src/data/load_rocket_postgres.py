import os
from pathlib import Path
import psycopg2

REPO_ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = REPO_ROOT / "sql" / "schema"
DATA_DIR = REPO_ROOT / "data" / "rocket"

VIEW_SQL = REPO_ROOT / "sql" / "analytics" / "dashboard_views.sql"

COPY_TASKS = [
    ("raw.events", DATA_DIR / "events.csv", "event_ts_ms, visitor_id, event_type, item_id, transaction_id"),
    ("raw.item_properties", DATA_DIR / "item_properties_part1.csv", "property_ts_ms, item_id, property, value"),
    ("raw.item_properties", DATA_DIR / "item_properties_part2.csv", "property_ts_ms, item_id, property, value"),
    ("raw.category_tree", DATA_DIR / "category_tree.csv", "category_id, parent_id"),
]


def run_sql_file(cursor, path: Path) -> None:
    with path.open("r", encoding="utf-8") as f:
        lines = []
        for line in f:
            if line.lstrip().startswith("\\"):
                continue
            lines.append(line)
        cursor.execute("".join(lines))


def copy_csv(cursor, table: str, path: Path, columns: str) -> None:
    with path.open("r", encoding="utf-8") as f:
        cursor.copy_expert(
            f"COPY {table} ({columns}) FROM STDIN WITH (FORMAT csv, HEADER true)",
            f,
        )


def main() -> None:
    db_url = os.getenv("DATABASE_URL", "postgresql://localhost:5432/rocket")
    conn = psycopg2.connect(db_url)
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            run_sql_file(cur, SQL_DIR / "00_raw_tables.sql")
            cur.execute("TRUNCATE raw.events, raw.item_properties, raw.category_tree;")
            conn.commit()

            for table, path, columns in COPY_TASKS:
                copy_csv(cur, table, path, columns)
                conn.commit()

            run_sql_file(cur, SQL_DIR / "10_curated_tables.sql")
            run_sql_file(cur, SQL_DIR / "20_build_curated.sql")
            run_sql_file(cur, VIEW_SQL)
            conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
