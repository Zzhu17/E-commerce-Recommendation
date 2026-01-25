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
    replaced = False
    for line in lines:
        if line.strip().startswith("Single-run sanity check"):
            out.append(
                f"Single-run sanity check (seed=42, sample_mod=200, candidate_size=2000, K=10): "
                f"NDCG@10 popularity {pop_ndcg:.4f}, collaborative filtering {cf_ndcg:.4f}"
            )
            replaced = True
        else:
            out.append(line)
    if not replaced:
        out.append(
            f"Single-run sanity check (seed=42, sample_mod=200, candidate_size=2000, K=10): "
            f"NDCG@10 popularity {pop_ndcg:.4f}, collaborative filtering {cf_ndcg:.4f}"
        )
    README_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket"),
    )
    parser.add_argument("--sample-mod", type=int, default=200)
    parser.add_argument("--candidate-size", type=int, default=2000)
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-end", default="2015-06-01")
    parser.add_argument("--val-end", default="2015-06-15")
    args = parser.parse_args()

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
