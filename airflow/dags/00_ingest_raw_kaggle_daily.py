from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator

from airflow.plugins.slack_callbacks import notify_slack

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET = "retailrocket/ecommerce-dataset"

with DAG(
    dag_id="00_ingest_raw_kaggle_daily",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args={"owner": "data"},
    sla_miss_callback=notify_slack,
) as dag:
    download = BashOperator(
        task_id="download_kaggle",
        bash_command=(
            "python pipelines/ingest/kaggle_download.py "
            "--dataset '{{ params.dataset }}'"
        ),
        params={"dataset": DATASET},
        cwd=str(REPO_ROOT),
    )

    load_raw = BashOperator(
        task_id="load_raw_tables",
        bash_command=(
            "python pipelines/ingest/load_raw.py "
            "--batch-id '{{ ds }}' "
            "--manifest data/raw/kaggle/retailrocket_ecommerce-dataset/{{ ds }}/ingest_manifest.json"
        ),
        cwd=str(REPO_ROOT),
    )

    dq_raw = BashOperator(
        task_id="dq_raw",
        bash_command=(
            "python pipelines/dq/run_ge.py --stage raw --batch-id '{{ ds }}'"
        ),
        cwd=str(REPO_ROOT),
    )

    download >> load_raw >> dq_raw
