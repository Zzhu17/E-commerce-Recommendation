# Runtime Hardening Baseline

- CI 启用 SCA（`pip-audit --strict`）与镜像 CVE 扫描（Trivy），`HIGH/CRITICAL` 阻断发布。
- 业务容器默认非 root 运行，生产环境启用只读根文件系统。
- 最小能力原则：默认 `cap_drop: [ALL]`，仅网关保留 `NET_BIND_SERVICE`。
- Postgres/Redis 在生产仅内网访问，不对公网直接暴露端口。
- 生产数据库连接强制 TLS（`sslmode=require` + CA 校验）。
- 备份需加密并定期做恢复演练，产出 `RPO/RTO` 指标。
