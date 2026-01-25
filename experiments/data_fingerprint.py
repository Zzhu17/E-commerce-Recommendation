import csv
import hashlib
from pathlib import Path

import json

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data" / "rocket"
OUTPUT_PATH = REPO_ROOT / "artifacts" / "data_fingerprint.json"


def file_hash(path: Path, algo="sha256") -> str:
    h = hashlib.new(algo)
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def count_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as f:
        return sum(1 for _ in f) - 1


def event_time_range(path: Path):
    min_ts = None
    max_ts = None
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = int(row["timestamp"])
            if min_ts is None or ts < min_ts:
                min_ts = ts
            if max_ts is None or ts > max_ts:
                max_ts = ts
    return min_ts, max_ts


def event_entity_counts(path: Path):
    users = set()
    items = set()
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            users.add(row["visitorid"])
            items.add(row["itemid"])
    return len(users), len(items)


def main():
    files = [
        DATA_DIR / "events.csv",
        DATA_DIR / "item_properties_part1.csv",
        DATA_DIR / "item_properties_part2.csv",
        DATA_DIR / "category_tree.csv",
    ]
    fingerprint = {"files": []}

    for path in files:
        fingerprint["files"].append(
            {
                "name": path.name,
                "size_bytes": path.stat().st_size,
                "rows": count_rows(path),
                "sha256": file_hash(path),
            }
        )

    events_path = DATA_DIR / "events.csv"
    min_ts, max_ts = event_time_range(events_path)
    users, items = event_entity_counts(events_path)
    fingerprint["events_time_range_ms"] = {
        "min": min_ts,
        "max": max_ts,
    }
    fingerprint["events_entities"] = {
        "unique_users": users,
        "unique_items": items,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(fingerprint, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
