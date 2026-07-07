---
name: maintain-repo-wiki
description: 构建和维护代码仓库/微服务系统的持久化 Markdown 知识库。用于单仓库 Repo Mode、集中式 Knowledge Repo Mode 和跨仓库 System Mode；要求知识库从面到点覆盖整体架构、服务边界、业务流程、字段传播、状态副作用、依赖失败影响、可信 API reference、IDL/source contract、配置/缓存、metrics/logs/alerts/owner 等运行时信息、troubleshooting runbook、历史背景和可复用业务咨询 answers，使知识库能替代研发回答业务咨询、历史背景、变更影响和排障指导问题。
---

# Maintain Repo Wiki

使用这个 skill 为单个代码仓库或一组微服务仓库创建持久化知识库。默认采用“从面到点的工程知识库”：先建立系统架构、服务边界和源码地图，再向下钻到业务流程、字段传播、状态副作用、接口契约、依赖失败影响和运行时排障证据。

核心目标：让 wiki 同时服务新人理解、接口对接、业务咨询、历史背景追问、需求修改、跨服务影响分析和线上排障。回答业务问题时，wiki 应能说明“这个字段/状态/请求从哪里来、被谁改写、传给谁、影响什么、异常时看哪些 metrics/logs、如何排查”。Karpathy Project Wiki 的长期问答沉淀保留在 `queries/`，但单仓库默认输出以工程手册 + 业务流程手册为主。

## 三种模式

### Repo Mode（单仓库）

用于当前仓库自己的知识库，默认输出：

```text
wiki/
├── index.md
├── log.md
├── SCHEMA.md
├── overview.md
├── source-map.md
├── components/
│   ├── config-and-cache.md
│   └── external-dependencies.md
├── flows/
│   ├── auth-and-identity.md
│   ├── business-flows.md
│   ├── field-propagation.md
│   └── runtime-observability.md
├── apis/
│   └── http-endpoints.md
├── runbooks/
│   └── request-troubleshooting.md
├── queries/
├── questions/
│   ├── idl-source-location.md
│   └── operations-metadata.md
└── decisions/
```

运行：

```bash
python3 <skill>/scripts/init_repo_wiki.py <repo-root>
```

### System Mode（跨仓库系统 wiki）

用于只维护跨服务全局知识，不存每个仓库的完整 wiki。默认输出 `system-wiki/`：

```bash
python3 <skill>/scripts/init_repo_wiki.py <root> --mode system
```

### Knowledge Repo Mode（集中式知识库仓库）

用于新建一个专门的知识库仓库，同时存每个输入仓库的知识库和全局系统知识库。默认输出：

```text
knowledge-repo/
├── sources.yaml
├── repos/
│   └── <repo-name>/wiki/
└── system/
    └── wiki/
```

运行示例：

```bash
python3 <skill>/scripts/init_repo_wiki.py <knowledge-repo-root> --mode knowledge \
  --repo https://code.example.com/example/mock_feed_service \
  --repo /abs/path/to/local/repo
```

## 核心规则

- 始终把当前源码、IDL/source contract、仓库内文档和用户提供上下文当作事实源。
- 单仓库事实写入 `wiki/`；集中式知识库中，每个仓库事实写入 `repos/<repo-name>/wiki/`，而且每个仓库都应保持同样的工程手册深度。
- 跨仓库事实写入 `system/wiki/`，例如 service catalog、dependency graph、contracts、end-to-end request flows、cross-service runbooks。
- 不要复制完整源码；只沉淀可验证知识、源码引用、接口契约、运行时关系和未决问题。
- 先用 wiki 快速定位，再回到源码或 contract 验证关键结论。
- 从面到点组织知识：先有 architecture/service catalog/dependency graph，再有 repo overview/source-map，再有 business flows、field propagation、API、config/cache、runbook 和 queries。
- Flow 不只写 auth/identity。每个核心业务入口都应有业务流程页，说明参数如何进入、如何校验/映射/传播、调用哪些组件、产生哪些状态副作用、失败如何表现，以及用哪些 metrics/logs 验证。
- 对用户反复追问的问题，沉淀到 `queries/`，并反向链接到 flow/API/runbook，使 wiki 能复用回答业务咨询和历史背景。
- 新增或明显修改页面时，同步更新 `index.md` 和 `log.md`。
- 不确定的信息写入 `questions/`，不要猜。
- 默认使用中文正文；代码标识符、文件路径、API 字段、配置 key、日志字段、metrics、alert、服务名和错误码保留英文原文。

## 页面组织

- `index.md`：知识库入口，按组件、流程、API、runbook、未决问题组织。
- `overview.md`：仓库职责、技术栈、目录地图、入口点和架构概览。
- `source-map.md`：源码区域到 wiki 页面的映射，帮助判断改代码后更新哪页。
- `components/`：服务外壳、middleware、handler/client、配置缓存、外部依赖等工程组件。
- `flows/`：业务流程、字段传播、认证身份、核心请求、数据写入、后台任务、跨组件执行序列、运行时可观测性。
- `apis/`：HTTP/RPC/CLI/event/schema 等 endpoint/interface 级别参考。
- `runbooks/`：排障手册、调试流程、上线检查、事故响应。
- `queries/`：值得长期保留的问题答案和分析。
- `questions/`：待确认的信息，例如 IDL 位置、owner/dashboard/alert 来源。
- `decisions/`：架构决策和取舍。

## 工程手册 Profile

每个仓库的首轮 wiki 应尽量达到这个效果：

- API 页面不是路由清单，而是 endpoint/interface reference：route、method、handler、IDL/source contract、字段表、字段来源、必填性、响应结构、错误行为和示例。
- Flow 页面说明入口、middleware/handler 序列、身份来源、状态副作用、失败模式和验证记录。
- Component 页面说明职责、关键源码、公开接口、依赖、失败影响和变更注意事项。
- Business flow 页面说明用户/业务问题对应的端到端逻辑：入口、字段来源、校验/映射、分支、组件调用、下游请求构造、状态副作用、输出、失败模式、metrics/logs、排查入口。
- Field propagation 页面说明关键业务字段从 HTTP/RPC/event/config 到下游依赖的传播矩阵，能回答“某参数是否透传给某依赖、在哪被改写、缺失如何兜底”。
- External dependency 页面说明依赖类型、强弱依赖、超时/错误处理、降级路径和用户可见影响。
- Config/cache 页面说明配置源、JSON shape、默认值、runtime impact、测试流量开关、cache key、TTL 和失效路径。
- Runbook 页面说明 symptoms、owners、metrics dashboards、alerts、common error logs、fast checks、mitigations 和 escalation。
- 无法确认的 IDL/source contract、owner、dashboard、alert、日志入口等，必须写入 `questions/` 并记录搜索证据。

## 工作流

### Bootstrap（初始化）

1. 对单仓库，运行 Repo Mode 并阅读 `rg --files`、README、CLAUDE.md、package manifest、build config、route definition、service entry point、config、IDL/source contract 和测试。
2. 对知识库仓库，运行 Knowledge Repo Mode，先写 `sources.yaml`，再为每个输入仓库生成 `repos/<repo-name>/wiki/`，同时生成 `system/wiki/`。
3. 首批页面优先填实 `overview.md`、`source-map.md`、`components/config-and-cache.md`、`components/external-dependencies.md`、`flows/auth-and-identity.md`、`flows/business-flows.md`、`flows/field-propagation.md`、`flows/runtime-observability.md`、主要 `apis/` 和最高风险 `runbooks/`。
4. 根据源码继续补仓库特有组件和核心业务流程，例如 `components/request-middleware.md`、`components/<domain>-adapter.md`、`flows/<domain>-request.md`、`flows/<domain>-pipeline.md`、`flows/<dependency>-request-build.md`。不要停留在 auth flow；如果服务有 feed/order/payment/search/collect/impression 等业务链路，必须写业务流程。
5. 跨仓库首批页面优先写 `system/wiki/service-catalog.md`、`dependency-graph.md`、关键 `contracts/`、端到端 `request-flows/`、`field-flows/` 和跨服务 runbook，并链接回各 `repos/<repo-name>/wiki/` 详细页面。
6. 只写能验证的信息；缺失信息写入 `questions/`，并记录搜索路径或命令。
7. 运行 `git status --short wiki system repos sources.yaml`，告诉用户哪些知识库文件还没纳入版本控制。

### Ingest（吸收代码或文档）

1. 明确目标范围：文件、模块、diff、PR、issue、设计文档、IDL/source contract 或用户提供材料。
2. 先读原始源码/契约/材料，再写 wiki。
3. 更新最小相关页面，避免顺手改无关内容。
4. 在 frontmatter 中优先用 `source_files` 记录源码引用；兼容旧页时可保留 `related_files`。集中式知识库还应记录 `repo`、`repo_url`、`verified_commit`。
5. 如果产生有长期价值的问答综合，写入 `queries/`。

### Deepen（深化）

当 wiki 已适合入门，但还不足以支撑接口对接、需求修改、运维排障时：

1. 把 API 总览升级为 endpoint/interface 级别 reference，补字段表、字段来源、必填性、错误行为、IDL source 和示例。
2. 定位源 IDL 或生成契约输入；找不到时，在 `questions/idl-source-location.md` 记录搜索证据。
3. 为外部依赖补页面，说明依赖类型、强弱依赖、超时/错误处理、降级和用户可见影响。
4. 为配置、缓存和 runbook 补 JSON 示例、默认值、运行时影响、测试开关、dashboard、alert、owner、常见错误日志和缓解步骤。
5. 为核心业务入口补 business flow 和 field propagation：逐字段列出来源、映射、默认值、传递到的内部对象、下游 RPC/event/cache 字段、是否用于过滤/排序/记录、缺失或异常时的表现。
6. 为运行时补 observability：metrics name/tag、log pattern、request id、dashboard/alert、常见异常样例、如何从症状定位到组件或依赖。
7. 在 `system/wiki/` 中补 producer/consumer、跨服务失败影响、end-to-end request flow、跨仓库字段传播矩阵和跨服务排障路径。

### Query（回答问题）

1. 先读当前层级的 `index.md`。
2. 对单仓库问题，读 `wiki/` 或 `repos/<repo>/wiki/` 的相关页面。
3. 对跨服务问题，读 `system/wiki/`，再按需跳到对应 `repos/<repo>/wiki/` 和源码/contract。
4. 对业务字段/流程问题，优先读 `flows/field-propagation.md`、相关 `flows/<domain>*.md`、API 字段表、config/cache 和 dependency/runbook；不要只读 auth flow。
5. 对关键结论回到源码、IDL/source contract、metrics/logs 或用户提供事实核验。
6. 如果 wiki 无法回答，明确指出缺口，补一个 `queries/<question>.md` 或更新 flow/field propagation 页面；不要让同类问题下次仍然回答不了。
7. 如果答案有长期价值，沉淀到 `queries/`，并更新 `index.md` 与 `log.md`。

### Refresh（代码变更后刷新）

1. 运行 `python3 <skill>/scripts/changed_files.py --wiki wiki` 或指定 `repos/<repo>/wiki`。
2. 重新阅读受影响源码文件。
3. 如果职责、行为、接口、依赖或运行时影响变化，更新相关页面。
4. 如果影响跨服务 contract、dependency graph 或 request flow，同步更新 `system/wiki/`。

### Lint（健康检查）

运行：

```bash
python3 <skill>/scripts/wiki_lint.py wiki
python3 <skill>/scripts/wiki_lint.py wiki --quality
```

基础 lint 发现缺 frontmatter、断链、孤儿页、缺失 source file、残留 `TODO/TBD/FIXME` 等问题。`--quality` 检查 API、依赖、配置、auth/identity、runbook 是否足以支撑接口对接、运行时理解和排障。具体规则见 `references/lint-rules.md`。

## 脚本

- `scripts/init_repo_wiki.py`：初始化 Repo/System/Knowledge Repo 三种模式。
- `scripts/wiki_lint.py`：检查 wiki 健康度和质量门槛。
- `scripts/changed_files.py`：把变更源码文件映射到引用它们的 wiki 页面，支持 `source_files` 和 `related_files`。
- `scripts/wiki_inventory.py`：输出页面元数据 JSON，便于审计或自动化。
