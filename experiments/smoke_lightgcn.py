import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

try:
    import torch  # noqa: F401
except Exception:
    raise SystemExit("torch not installed; skip LightGCN smoke test")

from src.pipelines.offline_eval import EvalConfig, evaluate_config


def main():
    db_url = os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket")
    os.environ["DATABASE_URL"] = db_url

    cfg = EvalConfig(
        train_end="2015-06-01",
        val_end="2015-06-15",
        sample_mod=2000,
        candidate_size=500,
        k=5,
        seed=42,
        bootstrap_enabled=False,
        bootstrap_resamples=0,
        models=[
            {"name": "popularity", "params": {}},
            {
                "name": "lightgcn",
                "params": {
                    "dim": 16,
                    "num_layers": 1,
                    "num_neg": 1,
                    "lr": 1e-3,
                    "batch_size": 512,
                    "epochs": 2,
                    "eval_k": 5,
                    "eval_every": 1,
                    "patience": 1,
                    "score_batch": 256,
                },
            },
        ],
    )

    metrics, _, _ = evaluate_config(cfg)
    if not metrics:
        raise RuntimeError("No metrics returned from LightGCN smoke test.")

    print("Smoke test OK")


if __name__ == "__main__":
    main()
