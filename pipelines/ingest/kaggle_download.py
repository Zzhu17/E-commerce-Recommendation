import argparse
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

import kagglehub


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def list_files(base: Path):
    files = []
    for p in base.rglob("*"):
        if p.is_file():
            files.append(
                {
                    "path": str(p.relative_to(base)),
                    "size_bytes": p.stat().st_size,
                    "sha256": sha256_file(p),
                }
            )
    return files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="retailrocket/ecommerce-dataset")
    parser.add_argument("--out-dir", default="data/raw/kaggle")
    args = parser.parse_args()

    download_path = Path(kagglehub.dataset_download(args.dataset))
    ds = datetime.utcnow().strftime("%Y%m%d")
    target_dir = Path(args.out_dir) / args.dataset.replace("/", "_") / ds
    target_dir.mkdir(parents=True, exist_ok=True)

    # copy files into raw zone for auditability
    for p in download_path.iterdir():
        if p.is_file():
            (target_dir / p.name).write_bytes(p.read_bytes())

    manifest = {
        "dataset": args.dataset,
        "downloaded_at": datetime.utcnow().isoformat(),
        "source_path": str(download_path),
        "target_dir": str(target_dir),
        "files": list_files(target_dir),
    }
    manifest_path = target_dir / "ingest_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Saved manifest to {manifest_path}")


if __name__ == "__main__":
    main()
