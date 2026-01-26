import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import psycopg2

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "artifacts" / "diagnostics"
DOC_PATH = REPO_ROOT / "docs" / "data_diagnostics.md"


def load_counts():
    db_url = os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket")
    with psycopg2.connect(db_url) as conn:
        user_counts = pd.read_sql_query(
            """
            SELECT user_id, COUNT(*) AS interactions
            FROM analytics.fact_events
            GROUP BY user_id
            """,
            conn,
        )
        item_counts = pd.read_sql_query(
            """
            SELECT product_id, COUNT(*) AS interactions
            FROM analytics.fact_events
            GROUP BY product_id
            """,
            conn,
        )
    return user_counts, item_counts


def plot_user_history(user_counts: pd.DataFrame, out_path: Path):
    plt.figure()
    plt.hist(user_counts["interactions"], bins=50, color="#4c78a8")
    plt.title("User Interaction History")
    plt.xlabel("Interactions per user")
    plt.ylabel("User count")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_item_longtail(item_counts: pd.DataFrame, out_path: Path):
    sorted_counts = item_counts.sort_values("interactions", ascending=False)
    plt.figure()
    plt.plot(range(1, len(sorted_counts) + 1), sorted_counts["interactions"], color="#f58518")
    plt.yscale("log")
    plt.xscale("log")
    plt.title("Item Popularity Long Tail")
    plt.xlabel("Item rank (log)")
    plt.ylabel("Interactions (log)")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    user_counts, item_counts = load_counts()

    user_plot = OUTPUT_DIR / "user_history_hist.png"
    item_plot = OUTPUT_DIR / "item_popularity_longtail.png"
    plot_user_history(user_counts, user_plot)
    plot_item_longtail(item_counts, item_plot)

    n_users = len(user_counts)
    n_items = len(item_counts)
    total_interactions = int(user_counts["interactions"].sum())
    sparsity = 1.0 - (total_interactions / (n_users * n_items))

    top_1pct = max(int(n_items * 0.01), 1)
    top_share = (
        item_counts.sort_values("interactions", ascending=False)
        .head(top_1pct)["interactions"]
        .sum()
        / total_interactions
    )

    md_lines = [
        "# Data Diagnostics",
        "",
        f"- users: {n_users}",
        f"- items: {n_items}",
        f"- interactions: {total_interactions}",
        f"- sparsity: {sparsity:.6f}",
        f"- top 1% items interaction share: {top_share:.2%}",
        "",
        "## Plots",
        f"- {user_plot.relative_to(REPO_ROOT)}",
        f"- {item_plot.relative_to(REPO_ROOT)}",
    ]
    DOC_PATH.write_text("\n".join(md_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
