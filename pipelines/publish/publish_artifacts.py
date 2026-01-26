import argparse
import hashlib
import json
import os
from pathlib import Path

import psycopg2


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def upload_minio(local_path: Path, bucket: str, prefix: str) -> str:
    import boto3

    endpoint = os.getenv("MINIO_ENDPOINT")
    access_key = os.getenv("MINIO_ACCESS_KEY")
    secret_key = os.getenv("MINIO_SECRET_KEY")
    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    key = f"{prefix}/{local_path.name}"
    s3.upload_file(str(local_path), bucket, key)
    return f"s3://{bucket}/{key}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket"))
    args = parser.parse_args()

    artifact_dir = Path(args.artifact_dir)
    use_minio = bool(os.getenv("MINIO_ENDPOINT"))
    bucket = os.getenv("MINIO_BUCKET", "reco-artifacts")
    prefix = f"{args.run_id}"

    conn = psycopg2.connect(args.database_url)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute(Path("sql/ml/30_ml_tables.sql").read_text())
            for p in artifact_dir.rglob("*"):
                if p.is_file():
                    uri = str(p)
                    if use_minio:
                        uri = upload_minio(p, bucket, prefix)
                    cur.execute(
                        "INSERT INTO ml.artifacts (run_id, artifact_type, uri, checksum) VALUES (%s,%s,%s,%s)",
                        (args.run_id, p.suffix.lstrip("."), uri, sha256_path(p)),
                    )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
