from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator

REPO_ROOT = Path(__file__).resolve().parents[2]

with DAG(
    dag_id="10_build_warehouse_daily",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args={"owner": "data"},
) as dag:
    build = BashOperator(
        task_id="build_stg_and_marts",
        bash_command="python pipelines/warehouse/build_warehouse.py",
        cwd=str(REPO_ROOT),
    )

    dq_stg = BashOperator(
        task_id="dq_stg",
        bash_command="python pipelines/dq/run_ge.py --stage stg",
        cwd=str(REPO_ROOT),
    )

    build >> dq_stg
