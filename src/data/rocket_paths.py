from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def resolve_rocket_data_dir() -> Path:
    env_dir = os.getenv("ROCKET_DATA_DIR")
    if env_dir:
        path = Path(env_dir).expanduser()
        if path.exists():
            return path

    local_dir = REPO_ROOT / "data" / "rocket"
    if local_dir.exists():
        return local_dir

    try:
        import kagglehub
    except Exception as exc:  # pragma: no cover - runtime dependency
        raise RuntimeError(
            "RetailRocket dataset not found. Set ROCKET_DATA_DIR or install kagglehub."
        ) from exc

    download_path = kagglehub.dataset_download("retailrocket/ecommerce-dataset")
    return Path(download_path)
