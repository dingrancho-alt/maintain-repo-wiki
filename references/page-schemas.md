# 页面 Schema

这些 schema 用于 `wiki/`、`repos/<repo>/wiki/` 和 `system/wiki/`。默认采用工程手册型页面：frontmatter 保持机器可读，正文保持中文、细节充分、结论可追溯。

## 通用 Frontmatter

单仓库页面：

```yaml
---
title: Human readable title
type: overview | component | flow | api | runbook | query | question | decision
status: active | draft | retired
source_files:
  - path/from/repo/root.ext
last_verified_commit: commit-or-unknown
last_verified: YYYY-MM-DD
tags:
  - short-tag
---
```

兼容规则：

- `source_files` 是新页面首选字段，用于表达页面结论直接核验过的源码文件。
- `related_files` 仍可使用，脚本会识别它，主要兼容 Karpathy Project Wiki 风格页面。
- 如果页面只记录外部运行时信息或跨仓库关系，可以不强行填源码，但必须链接到 repo wiki、contract 或 question。

集中式知识库中的仓库页面额外加：

```yaml
repo: mock_feed_service
repo_url: https://code.example.com/example/mock_feed_service
verified_commit: commit-or-unknown
```

规则：

- `source_files`/`related_files` 使用对应源码仓库根目录相对路径。
- 页面仍有未解决事实时，使用 `status: draft`。
- 仅对历史知识使用 `status: retired`。
- 一个页面只描述一个边界清晰的概念。
- 默认中文正文；代码符号、路径、字段名、配置 key、日志字段、metrics、alert、错误码保留英文原文。

## Repo Wiki 页面

- `overview`：仓库职责、技术栈、目录地图、架构概览。
- `component`：模块、服务、handler、client、配置对象、缓存、外部依赖。
- `flow`：业务流程、字段传播、认证、数据流、请求链路、错误处理、region 行为、缓存策略、架构模式、运行时可观测性。
- `api`：endpoint/interface 级别接口说明，包含 `IDL Source`、字段表、示例和错误行为。
- `runbook`：现象、owner、dashboard、alert、日志样例、快速检查、缓解和升级路径。
- `query`：值得长期保留的问题答案。
- `question`：无法确认的信息和下一步检查。
- `decision`：架构背景、决策、影响、备选方案和重新评估触发条件。

## Repo Wiki 默认页面

首轮初始化应创建这些页面，并在扫描源码后尽量填实，而不是只保留空目录：

- `index.md`：入口和所有重要页面链接。
- `overview.md`：仓库职责、技术栈、目录地图、入口点、架构和运行时备注。
- `source-map.md`：源码区域、对应 wiki 页面和说明。
- `components/config-and-cache.md`：配置源、JSON shape、默认值、运行时影响、测试流量开关、cache key、TTL、失效路径。
- `components/external-dependencies.md`：依赖矩阵、强弱依赖、超时/错误处理、失败影响、降级、日志指标、升级路径。
- `flows/auth-and-identity.md`：入口、middleware/handler 序列、身份来源、tenant/user/token/region 来源、失败模式。
- `flows/business-flows.md`：核心业务入口和业务流程索引，按业务问题组织，不只按代码目录组织。
- `flows/field-propagation.md`：关键字段从入口到内部对象、配置、下游依赖、缓存/event/response 的传播矩阵。
- `flows/runtime-observability.md`：业务流程对应的 metrics、logs、request id、dashboard、alert 和排障入口。
- `apis/http-endpoints.md`：路由表、IDL/source contract、endpoint 字段表、示例、错误码和调用方。
- `runbooks/request-troubleshooting.md`：现象、owner、fast checks、metrics dashboard、alert、常见错误日志、缓解和升级。
- `questions/idl-source-location.md`：IDL/source contract 搜索证据和当前最佳结论。
- `questions/operations-metadata.md`：owner/dashboard/alert/log source 的搜索证据和缺口。

## Section Requirements

API page：

- `Surface`
- `IDL Source`
- `Endpoint Reference`
- 字段表：`Field | Source | Required | Type | Description`
- `Identity Sources`，如果接口涉及认证、租户、token 或 request context
- `Example Request`
- `Example Response`
- `Errors And Status Codes`
- `Callers`

Component page：

- `Responsibility`
- `Key Files`
- `Public Interfaces`
- `Dependencies`
- `Failure Impact`
- `Change Notes`

Flow page：

- `Entry Points`
- `Middleware Or Handler Sequence` 或 `Sequence`
- `Business Context`，说明该流程回答哪些业务问题、历史背景或需求场景
- `Field Propagation`，如果流程涉及重要请求字段、配置字段、状态字段或下游请求字段
- `Identity Sources`，如果涉及认证/身份/租户
- `Runtime Observability`，说明 metrics/logs/request id/dashboard/alert
- `State And Side Effects`
- `Failure Modes`
- `Verification Notes`

Field propagation page：

- `Scope`
- 字段矩阵：`Field | Source | Validation Or Mapping | Internal Object | Downstream | Runtime Use | Missing Or Error Behavior`
- `Downstream Request Mapping`，说明字段是否进入 RPC/event/cache/search/sort 等下游请求
- `Config And Defaults`
- `Observability`
- `Open Questions`

Runbook：

- `Symptoms`
- `Owners`
- `Fast Checks`
- `Metrics Dashboards`
- `Alerts`
- `Common Error Logs`
- `Mitigations`
- `Escalation`

Question page：

- `Question`
- `Search Evidence`
- `Current Best Answer`
- `Next Checks`

## System Wiki 页面

- `service-catalog.md`：服务清单、repo、role、owner、wiki 链接、runtime。
- `dependency-graph.md`：上游、下游、协议、contract、failure impact 和 Mermaid 图。
- `contracts/`：跨服务 API/RPC/IDL/source contract、producer/consumer 和兼容性说明。
- `request-flows/`：端到端请求链路，按 service hop 说明行为和失败影响。
- `field-flows/`：跨服务字段传播，按关键业务字段说明来源、映射、下游使用、运行时证据和缺口。
- `runbooks/`：跨服务排障手册。
- `questions/`：跨仓库缺失事实，例如 owner、dashboard、alert、IDL 来源。

System wiki 只记录跨服务边界和全局运行时事实，不替代 `repos/<repo-name>/wiki/` 中的仓库内部细节。
