# 质量门槛

当第一版 wiki 已经能帮助新人入门，但还需要支撑接口对接、需求修改、跨服务理解或排障时，使用这些门槛判断下一步补什么。

## 完成度分层

### Level 1：Orientation（快速入门）

- 单仓库 `wiki/index.md` 链接所有重要页面。
- `overview.md` 说明职责、技术栈、目录地图和主要架构。
- `source-map.md` 把主要源码区域映射到 wiki 页面。
- 覆盖主要 entity 和核心 concept/request flow。
- 未知信息记录在 `questions/`。
- `wiki_lint.py` 通过。

### Level 2：Integration And Change Work（接口对接和需求修改）

- API 页面按 endpoint 或 interface 分开说明。
- 每个 endpoint 包含 method/route、handler、IDL source、字段表、字段来源、必填性、响应结构、错误行为和示例。
- 配置/缓存页面包含 JSON 结构、默认值、运行时影响和测试开关。
- 依赖页面区分 hard dependency 和 degradable dependency。
- auth/identity flow 说明 tenant、user、signature、token、region 或 request context 从哪里来。
- 核心业务入口有 business flow，不只停留在 auth/identity。
- 关键业务字段有 field propagation matrix，能回答“字段是否传给某下游依赖、在哪里被映射/默认/丢弃、异常时表现是什么”。
- `wiki_lint.py --quality` 通过，或所有剩余问题都有明确解释。

### Level 3：Operations And Troubleshooting（运行时和排障）

- runbook 覆盖常见失败现象、日志、metrics、fast checks、mitigation 和 escalation。
- 外部依赖页面说明 timeout、empty response、error propagation、fallback 和用户可见影响。
- 能确认时，runbook 包含 service owner、metrics dashboard、alert 名称和常见错误日志样例。
- 业务 flow 和 runtime observability 页面能把 metrics/logs 反向映射到业务阶段、组件和依赖。
- 对常见业务咨询和历史背景问题，`queries/` 有可复用答案，并链接回 flow/API/config/runbook。
- `log.md` 说明当前政策，并把过时记录标记为 superseded。
- wiki 已纳入 git，或用户明确决定只保留本地草稿。

### Level 4：System Knowledge（跨仓库知识）

- `sources.yaml` 记录所有输入仓库、source_type、url/path、branch、role、owner 和 scan_mode。
- `repos/<repo-name>/wiki/` 存每个仓库的局部知识。
- `system/wiki/service-catalog.md` 覆盖所有服务。
- `system/wiki/dependency-graph.md` 记录 upstream/downstream、protocol、contract 和 failure impact。
- `system/wiki/contracts/` 把 IDL/source contract 映射到 producer/consumer。
- `system/wiki/request-flows/` 记录端到端请求链路。
- `system/wiki/field-flows/` 记录跨服务关键字段传播和下游使用。
- 跨服务缺失事实记录在 `system/wiki/questions/`。

## 页面专项检查

API page：

- route-only table 只能作为起点，不能作为最终状态。
- 每个 endpoint 或 interface 使用独立小节。
- 写清 source IDL 路径，或解释字段来自哪里。
- 示例必须能从代码、测试、IDL 或文档中验证。
- 找不到 IDL 时，创建或更新 question 页面，不猜字段。

Dependency page：

- 包含 dependency name、client code、purpose、hard/degradable 分类、timeout/error behavior、fallback 和 user-visible impact。
- 只有能从仓库或用户上下文中确认时，才写 owner 或 escalation path。

System page：

- 不复制下游服务内部实现，只记录跨服务边界、contract、调用方向和失败影响。
- 内部细节链接到 `repos/<repo-name>/wiki/`。
- 对跨服务业务问题，必须有 request flow 或 field flow 能把字段、状态、依赖和运行时证据串起来。

Business flow page：

- 不能只列调用链；必须回答业务语义：输入是什么、为什么需要这一步、字段如何变化、输出影响什么。
- 包含关键字段表、分支条件、下游请求构造、状态副作用、失败模式、metrics/logs 和可验证 source files。
- 如果用户问过某个业务问题但 wiki 回答不了，优先补 flow/field propagation，再沉淀 query。

Field propagation page：

- 按字段而不是按代码函数组织。
- 至少覆盖主要入口的租户、身份、地域、语言/国家/设备、业务分类、内容 ID、状态/去重/实验等关键字段。
- 对每个字段说明是否进入下游 RPC/event/cache/search/sort；无法确认时明确写 `unknown` 并列 Next Check。

Runbook：

- 包含 owners、metrics dashboard、alert names、common error log samples、fast checks、mitigation 和 escalation。
- 如果运维元信息不在仓库中，记录到 `questions/` 并询问用户 owner/dashboard/alert 的来源，不要编造。

Maintenance log：

- 保留有价值的历史。
- 把过时政策标记为 superseded，并在附近说明当前政策。
- 记录保持简短且带日期。
