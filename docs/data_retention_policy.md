# Data Retention Policy & SOP

## Retention
- `feedback_events` 按 `created_at` 分层：`0-90=hot`、`91-180=warm`、`181-365=cold`、`>365=expired`。
- 定时任务执行：刷新 `storage_tier`，并批量删除 `>365` 天数据。

## DB Job & Audit
- 调度：`retention.cleanup.cron`
- 批次：`retention.cleanup.batch-size`
- 审计表：`retention_job_audit`

## User Deletion
- API：`POST /api/admin/privacy/delete-user`
- 入参：`userToken`、`reason`
- 动作：按 token 删除 `feedback_events`，写 `user_deletion_audit`

## Artifact TTL
- 配置：`retention.artifact.ttl-days`、`paths`、`include-extensions`
- 动作：删除超过 TTL 的 `.csv/.log/.json`

## SOP
```sql
select id, job_name, status, affected_rows, started_at, finished_at, details
from retention_job_audit
where job_name = 'retention_cleanup'
order by id desc
limit 20;
```

```sql
select id, user_token, deleted_rows, reason, requested_at
from user_deletion_audit
where user_token = :token
order by id desc;
```
