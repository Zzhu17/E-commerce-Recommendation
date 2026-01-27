from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator

from airflow.plugins.slack_callbacks import notify_slack, notify_failure

REPO_ROOT = Path(__file__).resolve().parents[2]

with DAG(
    dag_id="05_bootstrap_minio_daily",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args={"owner": "platform", "on_failure_callback": notify_failure},
    sla_miss_callback=notify_slack,
) as dag:
    bootstrap = BashOperator(
        task_id="bootstrap_minio_bucket",
        bash_command="python pipelines/publish/bootstrap_minio.py",
        cwd=str(REPO_ROOT),
    )

    bootstrap
