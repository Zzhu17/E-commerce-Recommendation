# Production 发布治理

## 强制发布门禁
`release-production.yml` 发布前必须通过：
- 单元测试
- 集成测试
- 依赖安全扫描（pip-audit）
- IaC 扫描（Checkov）

## 双人审批与变更审计
- `deploy-production` 绑定 GitHub `production` environment。
- 在仓库设置中为该 environment 配置 `Required reviewers = 2`。
- 每次发布产出 `production-release.json` 审计记录（发布人、commit、digest、时间）。

## 产物签名与部署验签
- 镜像使用 Cosign keyless 签名。
- 部署前执行 `scripts/verify_release_integrity.sh`，仅允许通过验签且带 digest 的镜像。
