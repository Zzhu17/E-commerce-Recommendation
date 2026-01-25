import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "experiments"


def get_latest_run() -> Path:
    runs = [p for p in ARTIFACTS_DIR.iterdir() if p.is_dir()]
    if not runs:
        raise FileNotFoundError("No experiment runs found in artifacts/experiments")
    return sorted(runs)[-1]


def summarize(df: pd.DataFrame) -> dict:
    pivot = df.pivot_table(
        index=["k", "candidate_size", "sample_mod", "seed"],
        columns="model",
        values=["hit_at_k", "ndcg_at_k", "coverage_at_k", "diversity_at_k"],
    )

    hit_wins = (pivot["hit_at_k"]["popularity"] > pivot["hit_at_k"]["user_cf"]).mean()
    cov_wins = (pivot["coverage_at_k"]["user_cf"] > pivot["coverage_at_k"]["popularity"]).mean()
    div_wins = (pivot["diversity_at_k"]["user_cf"] > pivot["diversity_at_k"]["popularity"]).mean()

    hit_gap = (pivot["hit_at_k"]["user_cf"] - pivot["hit_at_k"]["popularity"]).dropna()
    ndcg_gap = (pivot["ndcg_at_k"]["user_cf"] - pivot["ndcg_at_k"]["popularity"]).dropna()

    sensitivity = (
        df.groupby(["candidate_size", "model"])["coverage_at_k"].mean().unstack()
    )
    sensitivity_delta = (
        df.groupby(["candidate_size", "model"])["hit_at_k"].mean().unstack()
    )

    return {
        "hit_wins_ratio": float(hit_wins),
        "coverage_wins_ratio": float(cov_wins),
        "diversity_wins_ratio": float(div_wins),
        "hit_gap_mean": float(hit_gap.mean()),
        "hit_gap_std": float(hit_gap.std()),
        "ndcg_gap_mean": float(ndcg_gap.mean()),
        "ndcg_gap_std": float(ndcg_gap.std()),
        "coverage_by_candidate": sensitivity,
        "hit_by_candidate": sensitivity_delta,
        "hit_gap": hit_gap,
    }


def plot_hit_vs_k(df: pd.DataFrame, out_dir: Path):
    plt.figure()
    for model in df["model"].unique():
        subset = df[df["model"] == model]
        series = subset.groupby("k")["hit_at_k"].mean()
        plt.plot(series.index, series.values, marker="o", label=model)
    plt.title("Hit@K vs K")
    plt.xlabel("K")
    plt.ylabel("Hit@K")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "hit_vs_k.png")
    plt.close()


def plot_coverage_vs_candidate(df: pd.DataFrame, out_dir: Path):
    plt.figure()
    for model in df["model"].unique():
        subset = df[df["model"] == model]
        series = subset.groupby("candidate_size")["coverage_at_k"].mean()
        plt.plot(series.index, series.values, marker="o", label=model)
    plt.title("Coverage@K vs Candidate Size")
    plt.xlabel("Candidate Size")
    plt.ylabel("Coverage@K")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "coverage_vs_candidate_size.png")
    plt.close()


def plot_ndcg_vs_k(df: pd.DataFrame, out_dir: Path):
    plt.figure()
    for model in df["model"].unique():
        subset = df[df["model"] == model]
        series = subset.groupby("k")["ndcg_at_k"].mean()
        plt.plot(series.index, series.values, marker="o", label=model)
    plt.title("NDCG@K vs K")
    plt.xlabel("K")
    plt.ylabel("NDCG@K")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "ndcg_vs_k.png")
    plt.close()


def plot_delta_hit(df: pd.DataFrame, out_dir: Path):
    pivot = df.pivot_table(
        index=["k", "candidate_size", "sample_mod", "seed"],
        columns="model",
        values="hit_at_k",
    )
    delta = (pivot["user_cf"] - pivot["popularity"]).dropna()
    plt.figure()
    plt.hist(delta, bins=15, color="#4c78a8")
    plt.title("Delta Hit@K (user_cf - popularity)")
    plt.xlabel("Delta Hit@K")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(out_dir / "delta_hit_distribution.png")
    plt.close()


def plot_hit_by_segment(segment_df: pd.DataFrame, out_dir: Path):
    if segment_df.empty:
        return
    fig, ax = plt.subplots()
    pivot = (
        segment_df.groupby(["segment", "model"])["hit_at_k"].mean().unstack()
    )
    pivot.plot(kind="bar", ax=ax)
    ax.set_title("Hit@K by Segment")
    ax.set_xlabel("Segment")
    ax.set_ylabel("Hit@K")
    fig.tight_layout()
    fig.savefig(out_dir / "hit_by_segment.png")
    plt.close(fig)


def main(run_id=None):
    run_dir = ARTIFACTS_DIR / run_id if run_id else get_latest_run()
    results_path = run_dir / "results.csv"
    if not results_path.exists():
        print(f"Missing results.csv at {results_path}. Run experiments first.")
        return
    plots_dir = run_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(results_path)
    summary = summarize(df)

    summary_lines = [
        "# Experiment Summary",
        "",
        f"Run: {run_dir.name}",
        "",
        "## Overall comparisons",
        f"- Popularity Hit@K higher in {summary['hit_wins_ratio']:.1%} of configs",
        f"- User_CF Coverage higher in {summary['coverage_wins_ratio']:.1%} of configs",
        f"- User_CF Diversity higher in {summary['diversity_wins_ratio']:.1%} of configs",
        "",
        "## Stability",
        f"- Mean delta Hit@K (user_cf - popularity): {summary['hit_gap_mean']:.4f}",
        f"- Std delta Hit@K: {summary['hit_gap_std']:.4f}",
        f"- Mean delta NDCG@K (user_cf - popularity): {summary['ndcg_gap_mean']:.4f}",
        f"- Std delta NDCG@K: {summary['ndcg_gap_std']:.4f}",
        "",
        "## Sensitivity (candidate size)",
        summary["coverage_by_candidate"].to_string(),
        "",
        summary["hit_by_candidate"].to_string(),
        "",
        "## Recommendation",
        "- If popularity keeps winning Hit@K, consider hybrid ranking or add richer signals.",
        "- If user_cf increases coverage/diversity, use it for exploration or long-tail discovery.",
    ]

    (run_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    plot_hit_vs_k(df, plots_dir)
    plot_ndcg_vs_k(df, plots_dir)
    plot_coverage_vs_candidate(df, plots_dir)
    plot_delta_hit(df, plots_dir)

    segment_path = run_dir / "segment_results.csv"
    if segment_path.exists():
        segment_df = pd.read_csv(segment_path)
        plot_hit_by_segment(segment_df, plots_dir)

    manifest_path = run_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["summary_generated"] = True
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Summary written to {run_dir / 'summary.md'}")


if __name__ == "__main__":
    main()
