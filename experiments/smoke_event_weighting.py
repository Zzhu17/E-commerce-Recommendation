import os
from pathlib import Path

import pandas as pd
import psycopg2

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_events():
    db_url = os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket")
    sql = """
        SELECT user_id, product_id, event_type
        FROM analytics.fact_events
        WHERE event_type IN ('view', 'addtocart', 'transaction')
        LIMIT 10000
    """
    with psycopg2.connect(db_url) as conn:
        return pd.read_sql_query(sql, conn)


def apply_weighting(df: pd.DataFrame):
    weights = {"view": 1.0, "addtocart": 2.0, "transaction": 3.0}
    df["weight"] = df["event_type"].map(weights).fillna(1.0)
    return df


def main():
    df = load_events()
    df = apply_weighting(df)
    if df["weight"].isna().any():
        raise RuntimeError("Event weighting produced NaN values.")
    print("Event weighting smoke test OK")


if __name__ == "__main__":
    main()
