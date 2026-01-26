# Backfill Guide

## Airflow Backfill
```bash
airflow dags backfill -s 2025-01-01 -e 2025-01-07 00_ingest_raw_kaggle_daily
airflow dags backfill -s 2025-01-01 -e 2025-01-07 10_build_warehouse_daily
airflow dags backfill -s 2025-01-01 -e 2025-01-07 20_train_eval_publish_daily
```

## Manual Backfill (No Airflow)
```bash
python pipelines/ingest/kaggle_download.py --dataset retailrocket/ecommerce-dataset
python pipelines/ingest/load_raw.py --batch-id 2025-01-01 --manifest data/raw/kaggle/retailrocket_ecommerce-dataset/20250101/ingest_manifest.json
python pipelines/warehouse/build_warehouse.py
python pipelines/features/build_snapshot.py --ds 2025-01-01
```
