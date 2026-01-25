import json
import itertools
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.pipelines.offline_eval import EvalConfig, evaluate_config

ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "experiments"


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def build_grid(base_cfg: dict, grid_cfg: dict):
    grid = grid_cfg.get("grid", {})
    keys = sorted(grid.keys())
    values = [grid[k] for k in keys]
    for combo in itertools.product(*values):
        cfg = json.loads(json.dumps(base_cfg))
        for k, v in zip(keys, combo):
            if k in ("k",):
                cfg["eval"]["k"] = v
            elif k in ("candidate_size", "sample_mod"):
                cfg["data"][k] = v
            elif k == "seed":
                cfg["repro"]["seed"] = v
        yield cfg


def config_to_eval(cfg: dict) -> EvalConfig:
    return EvalConfig(
        train_end=cfg["data"]["temporal_split"]["train_end"],
        val_end=cfg["data"]["temporal_split"]["val_end"],
        sample_mod=cfg["data"]["sample_mod"],
        candidate_size=cfg["data"]["candidate_size"],
        k=cfg["eval"]["k"],
        seed=cfg["repro"]["seed"],
        bootstrap_enabled=cfg["eval"]["bootstrap"]["enabled"],
        bootstrap_resamples=cfg["eval"]["bootstrap"]["n_resamples"],
        models=cfg["models"],
    )


def main():
    if not os.getenv("DATABASE_URL"):
        print("DATABASE_URL is not set. Example:")
        print("export DATABASE_URL=\"postgresql://postgres:postgres@localhost:5432/rocket\"")
        return
    base_path = REPO_ROOT / "experiments" / "configs" / "base.yaml"
    grid_path = REPO_ROOT / "experiments" / "configs" / "grid_small.yaml"
    base_cfg = load_yaml(base_path)
    grid_cfg = load_yaml(grid_path)

    run_id = base_cfg["experiment"].get("run_id") or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_dir = ARTIFACTS_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    git_commit = get_git_commit()
    timestamp = datetime.utcnow().isoformat()

    results = []
    segment_results = []
    for cfg in build_grid(base_cfg, grid_cfg):
        eval_cfg = config_to_eval(cfg)
        metrics, segment_metrics, timing = evaluate_config(eval_cfg)
        for row in metrics:
            results.append(
                {
                    "run_id": run_id,
                    "timestamp": timestamp,
                    "git_commit": git_commit,
                    "model": row["model"],
                    "k": eval_cfg.k,
                    "candidate_size": eval_cfg.candidate_size,
                    "sample_mod": eval_cfg.sample_mod,
                    "seed": eval_cfg.seed,
                    "n_users": row["n_users"],
                    "n_items": row["n_items"],
                    "n_interactions": row["n_interactions"],
                    "hit_at_k": row["hit_at_k"],
                    "ndcg_at_k": row["ndcg_at_k"],
                    "coverage_at_k": row["coverage_at_k"],
                    "diversity_at_k": row["diversity_at_k"],
                    "hit_ci_low": row["hit_ci_low"],
                    "hit_ci_high": row["hit_ci_high"],
                    "train_seconds": row["train_seconds"],
                    "infer_seconds": row["infer_seconds"],
                    "total_seconds": timing["total_seconds"],
                }
            )
        if segment_metrics:
            for seg in segment_metrics:
                seg.update(
                    {
                        "run_id": run_id,
                        "timestamp": timestamp,
                        "git_commit": git_commit,
                    }
                )
            segment_results.extend(segment_metrics)

    df = pd.DataFrame(results)
    df.to_csv(out_dir / "results.csv", index=False)
    if base_cfg["experiment"].get("save_parquet", True):
        df.to_parquet(out_dir / "results.parquet", index=False)

    if segment_results:
        seg_df = pd.DataFrame(segment_results)
        seg_df.to_csv(out_dir / "segment_results.csv", index=False)

    manifest = {
        "run_id": run_id,
        "timestamp": timestamp,
        "git_commit": git_commit,
        "base_config": base_cfg,
        "grid_config": grid_cfg,
        "python": os.sys.version,
    }
    with (out_dir / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Saved results to {out_dir}")


if __name__ == "__main__":
    main()
