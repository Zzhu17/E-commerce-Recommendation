# Privacy Data Inventory（精简版）

## 1. 全链路字段盘点与敏感级别

> 分级：P0=可识别个人；P1=行为/画像相关；P2=系统与运维字段。

| 链路 | 字段 | 级别 | 当前策略 |
|---|---|---|---|
| 前端 `/api/recommendations` | `userId` | P0 | 仅在线请求使用，不落 `feedback_events` 明文 |
| 前端 `/api/recommendations` | `scene,size,requestId` | P1/P2 | 保留 |
| 前端 `/api/feedback` | `requestId,itemId,eventType,scene,ts` | P1/P2 | 业务必需，默认采集 |
| 前端 `/api/feedback` | `userId` | P0 | 入库前转不可逆 token |
| 前端 `/api/feedback` | `modelVersion,extra` | P2/不定 | 分析可选，默认不采集 |
| 后端日志 | `requestId,status,latency,path` | P2 | 保留；不打印请求 body |
| `feedback_events` | `user_id` | P0→P1 | 存 `tok_<saltVersion>_<digest>` |
| 候选表 `candidates` | `user_id` | P0 | 仍用于在线召回（后续可与 token 体系统一） |
| 模型输入 | `userId` | P0 | 当前仍传原值（下一阶段建议 token 化） |
| 模型输出 | `requestId,modelVersion,scores` | P1/P2 | 保留 |

## 2. `feedback_events` 字段策略（已落地）

配置约束：`user-token` 的 `active-salt-version/pepper/salts` 必填，缺失即启动失败（无 fallback）。

1. 默认不存可逆用户标识。
2. `user_id` 改为不可逆 token：`HMAC-SHA256(saltVersion:userId, pepper:salt)`。
3. 支持轮换盐：`active-salt-version + salts`。
4. 管理查询兼容：按原始 `userId` 查询时先同算法 token 化。

## 3. `extra` 白名单 Schema（已落地）

允许 key：`position`、`page`、`source`、`experiment_id`、`latency_ms`。

规则：
- 非白名单 key 丢弃；
- 仅保留标量值（string/number/boolean/null）；
- 对象/数组丢弃；
- `collect-optional-fields=false` 时整体不采集。

## 4. 必需字段 vs 可选字段

- **业务必需（默认采集）**：`requestId,userId(token),itemId,eventType,scene,ts`
- **分析可选（默认不采集）**：`modelVersion,extra`
- 开关：`privacy.feedback.collect-optional-fields=false`

## 5. 保留期限、访问角色、合法性依据（建议值）

| 数据对象 | 保留期限 | 访问角色 | 合法性依据 |
|---|---|---|---|
| `feedback_events`（去标识） | 180 天 | 推荐后端、数据分析（最小权限） | 履约 + 合法权益（效果评估） |
| API 日志（无 body） | 30 天 | SRE/后端 | 合法权益（审计/排障） |
| `candidates` | 30–90 天 | 推荐后端/离线任务 | 履约 |
| 模型推理日志（脱敏） | 30 天 | 推荐后端/模型工程 | 合法权益（质量监控） |
