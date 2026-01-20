import os
from pathlib import Path

import pandas as pd
import psycopg2

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "dashboards" / "powerbi" / "extracts"

EXPORTS = {
    "funnel_30d": "SELECT * FROM analytics.vw_funnel_30d",
    "segment_channel_30d": "SELECT * FROM analytics.vw_segment_channel_30d",
    "marketing_efficiency_30d": "SELECT * FROM analytics.vw_marketing_efficiency_30d",
    "cohort_weekly": "SELECT * FROM analytics.vw_cohort_weekly",
}


def main() -> None:
    db_url = os.getenv("DATABASE_URL", "postgresql://localhost:5432/rocket")
    conn = psycopg2.connect(db_url)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        for name, query in EXPORTS.items():
            df = pd.read_sql_query(query, conn)
            df.to_csv(OUTPUT_DIR / f"{name}.csv", index=False)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
