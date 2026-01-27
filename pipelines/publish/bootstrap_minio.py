import argparse
import os

import boto3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", default=os.getenv("MINIO_BUCKET", "reco-artifacts"))
    args = parser.parse_args()

    endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY", "minio")
    secret_key = os.getenv("MINIO_SECRET_KEY", "minio123")

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    buckets = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
    if args.bucket not in buckets:
        s3.create_bucket(Bucket=args.bucket)
        print(f"Created bucket {args.bucket}")
    else:
        print(f"Bucket {args.bucket} already exists")


if __name__ == "__main__":
    main()
