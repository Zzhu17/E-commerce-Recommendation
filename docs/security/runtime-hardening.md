# Runtime Hardening Baseline

## 1) 漏洞扫描与发布阻断
- CI 里增加了 SCA（`pip-audit --strict`）与镜像 CVE 扫描（Trivy）。
- 任何 `HIGH/CRITICAL` 漏洞会直接让流水线失败，阻断发布。

## 2) 容器最小权限
- 业务容器统一使用非 root 账号（uid/gid `10001`）。
- 生产编排启用 `read_only: true`，仅给 `/tmp` 挂载 `tmpfs`。
- 默认 `cap_drop: [ALL]`，仅网关保留 `NET_BIND_SERVICE` 用于 80/443 监听。
- 启用 `no-new-privileges:true`。

## 3) Postgres/Redis 内网访问
- `docker-compose.prod.yml` 中 Postgres/Redis 取消 `ports` 暴露，只留内部网络访问。
- 生产网络 `reco-net` 设为 `internal: true`。
- 云上部署时，仅允许应用子网/跳板机所在安全组访问数据库与缓存端口（白名单）。

## 4) 数据库 TLS（至少生产）
- 生产 Postgres 强制 `ssl=on`。
- Backend 连接串使用 `sslmode=require` 并挂载 CA 证书校验。

## 5) 备份加密与恢复演练（RPO/RTO）
- 新增 `scripts/backup_restore_drill.sh`：
  1. `pg_dump` 备份。
  2. 用 AES-256-CBC + PBKDF2 做加密。
  3. 解密后恢复到演练库。
  4. 输出 `rpo_seconds` 与 `rto_seconds` 指标。

## 推荐演练频率
- 生产：每周一次恢复演练。
- 变更窗口后：额外执行一次。
- 目标阈值（可按业务调整）：
  - `RPO <= 900s`
  - `RTO <= 1800s`
