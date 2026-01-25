import argparse
import os
from pathlib import Path
import sys

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.pipelines.offline_eval import EvalConfig, evaluate_config

README_PATH = REPO_ROOT / "README.md"
OUTPUT_PATH = REPO_ROOT / "artifacts" / "experiments" / "single_eval_results.csv"


def patch_readme(pop_ndcg: float, cf_ndcg: float) -> None:
    text = README_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    out = []
    for line in lines:
        if line.strip().startswith("| NDCG@10"):
            out.append(f"| NDCG@10 | {pop_ndcg:.4f} | {cf_ndcg:.4f} |")
        else:
            out.append(line)
    README_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL"))
    parser.add_argument("--sample-mod", type=int, default=200)
    parser.add_argument("--candidate-size", type=int, default=2000)
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-end", default="2015-06-01")
    parser.add_argument("--val-end", default="2015-06-15")
    args = parser.parse_args()

    if not args.database_url:
        raise SystemExit("DATABASE_URL not set. Use --database-url or export DATABASE_URL.")

    os.environ["DATABASE_URL"] = args.database_url

    cfg = EvalConfig(
        train_end=args.train_end,
        val_end=args.val_end,
        sample_mod=args.sample_mod,
        candidate_size=args.candidate_size,
        k=args.k,
        seed=args.seed,
        bootstrap_enabled=False,
        bootstrap_resamples=0,
        models=[
            {"name": "popularity", "params": {}},
            {"name": "user_cf", "params": {"top_neighbors": 50}},
        ],
    )

    metrics, _, _ = evaluate_config(cfg)
    df = pd.DataFrame(metrics)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    pop_ndcg = float(df[df["model"] == "popularity"]["ndcg_at_k"].iloc[0])
    cf_ndcg = float(df[df["model"] == "user_cf"]["ndcg_at_k"].iloc[0])
    patch_readme(pop_ndcg, cf_ndcg)
    print(f"Updated README NDCG@10 with popularity={pop_ndcg:.4f}, user_cf={cf_ndcg:.4f}")


if __name__ == "__main__":
    main()
