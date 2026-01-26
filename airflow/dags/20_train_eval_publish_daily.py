from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator

REPO_ROOT = Path(__file__).resolve().parents[2]

with DAG(
    dag_id="20_train_eval_publish_daily",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args={"owner": "ml"},
) as dag:
    snapshot = BashOperator(
        task_id="build_snapshot",
        bash_command="bash -c 'python pipelines/features/build_snapshot.py --ds {{ ds }} > /tmp/snapshot_id'",
        cwd=str(REPO_ROOT),
    )

    dq_edges = BashOperator(
        task_id="dq_edges",
        bash_command="python pipelines/dq/run_ge.py --stage edges --batch-id $(cat /tmp/snapshot_id)",
        cwd=str(REPO_ROOT),
    )

    train_lightgcn = BashOperator(
        task_id="train_lightgcn",
        bash_command="python pipelines/train/train_lightgcn.py --snapshot-id $(cat /tmp/snapshot_id)",
        cwd=str(REPO_ROOT),
    )

    train_als = BashOperator(
        task_id="train_als",
        bash_command="python pipelines/train/train_als.py --snapshot-id $(cat /tmp/snapshot_id)",
        cwd=str(REPO_ROOT),
    )

    eval_run = BashOperator(
        task_id="eval_offline",
        bash_command="python pipelines/eval/offline_eval.py --run-id dummy --snapshot-id $(cat /tmp/snapshot_id)",
        cwd=str(REPO_ROOT),
    )

    snapshot >> dq_edges >> [train_lightgcn, train_als] >> eval_run
