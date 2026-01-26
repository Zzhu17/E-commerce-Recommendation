import argparse
import json
import os
from pathlib import Path

import psycopg2


def run_sql(cursor, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    cursor.execute(sql)


def copy_to_temp(cursor, temp_table: str, path: Path, columns: str) -> None:
    cursor.execute(f"CREATE TEMP TABLE {temp_table} ({columns})")
    with path.open("r", encoding="utf-8") as f:
        cursor.copy_expert(
            f"COPY {temp_table} ({columns}) FROM STDIN WITH (FORMAT csv, HEADER true)",
            f,
        )


def insert_from_temp(cursor, temp_table: str, target_table: str, batch_id: str, columns: str) -> None:
    cols = ",".join([c.split()[0] for c in columns.split(",")])
    cursor.execute(
        f"INSERT INTO {target_table} (batch_id, {cols}) SELECT %s, {cols} FROM {temp_table}",
        (batch_id,),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket"))
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    data_dir = Path(manifest["target_dir"])

    conn = psycopg2.connect(args.database_url)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            run_sql(cur, Path("sql/raw/00_raw_ingest_tables.sql"))
            cur.execute(
                """
                INSERT INTO raw.ingest_batches (batch_id, dataset, dataset_version, downloaded_at, manifest_json)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (batch_id) DO NOTHING
                """,
                (
                    args.batch_id,
                    manifest.get("dataset"),
                    manifest.get("dataset_version"),
                    manifest.get("downloaded_at"),
                    json.dumps(manifest),
                ),
            )
            for f in manifest["files"]:
                cur.execute(
                    """
                    INSERT INTO raw.ingest_files (batch_id, file_name, file_hash, file_size)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (batch_id, file_name) DO NOTHING
                    """,
                    (args.batch_id, f["path"], f["sha256"], f["size_bytes"]),
                )

            events = data_dir / "events.csv"
            item_p1 = data_dir / "item_properties_part1.csv"
            item_p2 = data_dir / "item_properties_part2.csv"
            category = data_dir / "category_tree.csv"

            cur.execute("DELETE FROM raw.events_raw WHERE batch_id = %s", (args.batch_id,))
            cur.execute("DELETE FROM raw.item_properties_raw WHERE batch_id = %s", (args.batch_id,))
            cur.execute("DELETE FROM raw.category_tree_raw WHERE batch_id = %s", (args.batch_id,))

            if events.exists():
                columns = "event_ts_ms BIGINT, visitor_id BIGINT, event_type TEXT, item_id BIGINT, transaction_id BIGINT"
                copy_to_temp(cur, "tmp_events", events, columns)
                insert_from_temp(cur, "tmp_events", "raw.events_raw", args.batch_id, columns)

            if item_p1.exists():
                columns = "property_ts_ms BIGINT, item_id BIGINT, property TEXT, value TEXT"
                copy_to_temp(cur, "tmp_item_props1", item_p1, columns)
                insert_from_temp(cur, "tmp_item_props1", "raw.item_properties_raw", args.batch_id, columns)

            if item_p2.exists():
                columns = "property_ts_ms BIGINT, item_id BIGINT, property TEXT, value TEXT"
                copy_to_temp(cur, "tmp_item_props2", item_p2, columns)
                insert_from_temp(cur, "tmp_item_props2", "raw.item_properties_raw", args.batch_id, columns)

            if category.exists():
                columns = "category_id BIGINT, parent_id BIGINT"
                copy_to_temp(cur, "tmp_category", category, columns)
                insert_from_temp(cur, "tmp_category", "raw.category_tree_raw", args.batch_id, columns)

            conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
