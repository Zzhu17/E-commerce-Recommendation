from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from airflow.plugins.slack_callbacks import notify_slack, notify_failure

REPO_ROOT = Path(__file__).resolve().parents[2]


def fetch_latest_run(**context):
    import subprocess
    cmd = ["python", "pipelines/publish/get_latest_run.py", "--model-name", "lightgcn"]
    result = subprocess.check_output(cmd, cwd=str(REPO_ROOT), text=True)
    run_id = result.strip().splitlines()[-1]
    context["ti"].xcom_push(key="run_id", value=run_id)


with DAG(
    dag_id="30_publish_candidates_daily",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args={"owner": "serving", "on_failure_callback": notify_failure},
    sla_miss_callback=notify_slack,
) as dag:
    latest = PythonOperator(
        task_id="fetch_latest_run",
        python_callable=fetch_latest_run,
    )

    build_topk = BashOperator(
        task_id="build_topk",
        bash_command=(
            "python pipelines/publish/build_topk.py "
            "--run-id {{ ti.xcom_pull(task_ids='fetch_latest_run', key='run_id') }} "
            "--user-emb artifacts/{{ ti.xcom_pull(task_ids='fetch_latest_run', key='run_id') }}/user_emb.npy "
            "--item-emb artifacts/{{ ti.xcom_pull(task_ids='fetch_latest_run', key='run_id') }}/item_emb.npy "
            "--k 10 --output artifacts/user_topk.parquet"
        ),
        cwd=str(REPO_ROOT),
    )

    publish = BashOperator(
        task_id="publish_candidates",
        bash_command="python pipelines/publish/publish_candidates.py --run-id {{ ti.xcom_pull(task_ids='fetch_latest_run', key='run_id') }} --topk artifacts/user_topk.parquet",
        cwd=str(REPO_ROOT),
    )

    latest >> build_topk >> publish
