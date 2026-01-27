from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from airflow.plugins.slack_callbacks import notify_slack, notify_failure

REPO_ROOT = Path(__file__).resolve().parents[2]


def build_snapshot(ds, **context):
    import subprocess
    cmd = ["python", "pipelines/features/build_snapshot.py", "--ds", ds]
    result = subprocess.check_output(cmd, cwd=str(REPO_ROOT), text=True)
    snapshot_id = result.strip().splitlines()[-1]
    context["ti"].xcom_push(key="snapshot_id", value=snapshot_id)


def train_lightgcn(task_id, **context):
    import subprocess
    snapshot_id = context["ti"].xcom_pull(task_ids="build_snapshot", key="snapshot_id")
    cmd = ["python", "pipelines/train/train_lightgcn.py", "--snapshot-id", snapshot_id]
    result = subprocess.check_output(cmd, cwd=str(REPO_ROOT), text=True)
    run_id = result.strip().splitlines()[-1]
    context["ti"].xcom_push(key="run_id", value=run_id)


with DAG(
    dag_id="20_train_eval_publish_daily",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args={"owner": "ml", "on_failure_callback": notify_failure},
    sla_miss_callback=notify_slack,
) as dag:
    snapshot = PythonOperator(
        task_id="build_snapshot",
        python_callable=build_snapshot,
        op_kwargs={"ds": "{{ ds }}"},
    )

    dq_edges = BashOperator(
        task_id="dq_edges",
        bash_command="python pipelines/dq/run_ge.py --stage edges --batch-id '{{ ti.xcom_pull(task_ids=\"build_snapshot\", key=\"snapshot_id\") }}'",
        cwd=str(REPO_ROOT),
    )

    train_lgcn = PythonOperator(
        task_id="train_lightgcn",
        python_callable=train_lightgcn,
    )

    train_als = BashOperator(
        task_id="train_als",
        bash_command="python pipelines/train/train_als.py --snapshot-id '{{ ti.xcom_pull(task_ids=\"build_snapshot\", key=\"snapshot_id\") }}'",
        cwd=str(REPO_ROOT),
    )

    eval_run = BashOperator(
        task_id="eval_offline",
        bash_command="python pipelines/eval/offline_eval.py --run-id '{{ ti.xcom_pull(task_ids=\"train_lightgcn\", key=\"run_id\") }}' --snapshot-id '{{ ti.xcom_pull(task_ids=\"build_snapshot\", key=\"snapshot_id\") }}' --topk artifacts/{{ ti.xcom_pull(task_ids=\"train_lightgcn\", key=\"run_id\") }}/user_topk.parquet",
        cwd=str(REPO_ROOT),
    )

    snapshot >> dq_edges >> [train_lgcn, train_als] >> eval_run
