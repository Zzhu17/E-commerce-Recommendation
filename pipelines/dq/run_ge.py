import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import great_expectations as ge
import pandas as pd
import psycopg2


def load_df(conn, stage: str, batch_id: str):
    if stage == "raw":
        return pd.read_sql_query(
            """
            SELECT event_ts_ms, visitor_id, event_type, item_id
            FROM raw.events_raw
            WHERE batch_id = %s
            """,
            conn,
            params=(batch_id,),
        )
    if stage == "stg":
        return pd.read_sql_query(
            """
            SELECT event_ts, user_id, item_id, event_type, weight
            FROM stg.events
            """,
            conn,
        )
    if stage == "edges":
        return pd.read_sql_query(
            """
            SELECT user_idx, item_idx, weight
            FROM feat.train_edges
            WHERE snapshot_id = %s
            """,
            conn,
            params=(batch_id,),
        )
    raise ValueError("Unknown stage")


def run_expectations(df: pd.DataFrame, stage: str):
    gdf = ge.from_pandas(df)
    if stage == "raw":
        gdf.expect_table_row_count_to_be_greater_than(0)
        gdf.expect_column_values_to_not_be_null("event_type")
        gdf.expect_column_values_to_be_in_set("event_type", ["view", "addtocart", "transaction"])
        gdf.expect_column_values_to_not_be_null("event_ts_ms")
        gdf.expect_column_values_to_not_be_null("visitor_id")
        gdf.expect_column_values_to_not_be_null("item_id")
    elif stage == "stg":
        gdf.expect_table_row_count_to_be_greater_than(0)
        gdf.expect_column_values_to_be_greater_than("weight", 0)
        gdf.expect_column_values_to_not_be_null("event_ts")
        gdf.expect_column_values_to_not_be_null("user_id")
        gdf.expect_column_values_to_not_be_null("item_id")
    elif stage == "edges":
        gdf.expect_table_row_count_to_be_greater_than(0)
        gdf.expect_column_values_to_be_greater_than_or_equal_to("user_idx", 0)
        gdf.expect_column_values_to_be_greater_than_or_equal_to("item_idx", 0)
    result = gdf.validate()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, choices=["raw", "stg", "edges"])
    parser.add_argument("--batch-id", default=None)
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket"))
    args = parser.parse_args()

    conn = psycopg2.connect(args.database_url)
    conn.autocommit = False
    try:
        df = load_df(conn, args.stage, args.batch_id)
        result = run_expectations(df, args.stage)
        validation_id = f"{args.stage}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        with conn.cursor() as cur:
            cur.execute(Path("sql/dq/50_dq_tables.sql").read_text())
            cur.execute(
                """
                INSERT INTO dq.validation_results (validation_id, suite_name, run_at, success, result_json)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    validation_id,
                    f"{args.stage}_suite",
                    datetime.utcnow(),
                    bool(result.success),
                    json.dumps(result.to_json_dict()),
                ),
            )
        conn.commit()
        if not result.success:
            raise RuntimeError("DQ failed")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
