from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator

from airflow.plugins.slack_callbacks import notify_slack, notify_failure

REPO_ROOT = Path(__file__).resolve().parents[2]

with DAG(
    dag_id="30_publish_candidates_daily",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args={"owner": "serving", "on_failure_callback": notify_failure},
    sla_miss_callback=notify_slack,
) as dag:
    build_topk = BashOperator(
        task_id="build_topk",
        bash_command=(
            "python pipelines/publish/build_topk.py "
            "--run-id dummy --user-emb artifacts/dummy/user_emb.npy "
            "--item-emb artifacts/dummy/item_emb.npy --k 10 --output artifacts/user_topk.parquet"
        ),
        cwd=str(REPO_ROOT),
    )

    publish = BashOperator(
        task_id="publish_candidates",
        bash_command="python pipelines/publish/publish_candidates.py --run-id dummy --topk artifacts/user_topk.parquet",
        cwd=str(REPO_ROOT),
    )

    build_topk >> publish
