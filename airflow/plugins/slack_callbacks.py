import os
import json
import urllib.request


def notify_slack(context):
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook:
        return
    dag_id = context.get("dag", {}).dag_id if context.get("dag") else "unknown"
    task_id = context.get("task_instance").task_id if context.get("task_instance") else "unknown"
    message = {
        "text": f"Airflow SLA miss: {dag_id}.{task_id}"
    }
    data = json.dumps(message).encode("utf-8")
    req = urllib.request.Request(webhook, data=data, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req)
