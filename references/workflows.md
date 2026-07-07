# 工作流

## Repo Mode（单仓库）

1. 运行 `python3 <skill>/scripts/init_repo_wiki.py <repo-root>`。
2. 用 `rg --files` 了解仓库结构。
3. 阅读 README、CLAUDE.md、package manifest、build config、route definition、service entry point、handler/client、config、IDL/source contract 和测试。
4. 填实默认工程手册页：`overview.md`、`source-map.md`、`components/config-and-cache.md`、`components/external-dependencies.md`、`flows/auth-and-identity.md`、`apis/http-endpoints.md`、`runbooks/request-troubleshooting.md`。
5. 根据仓库实际结构补仓库特有页面，例如 `components/request-middleware.md`、`components/<domain>-adapter.md`、`flows/<domain>-request.md`、`flows/<write-path>.md`。
6. 把未知信息放入 `questions/`，记录搜索证据，不猜 owner、dashboard、alert、IDL 来源或外部调用方。
7. 运行 `git status --short wiki` 并报告状态。

## Knowledge Repo Mode（集中式知识库仓库）

1. 运行 `python3 <skill>/scripts/init_repo_wiki.py <knowledge-root> --mode knowledge --repo <url-or-path> ...`。
2. 检查 `sources.yaml`，补充每个 repo 的 role、owner、branch、scan_mode。
3. 对每个输入仓库，生成或更新 `repos/<repo-name>/wiki/`，并使用与单仓库相同的工程手册深度。
4. 对每个仓库至少填实 API、核心 flow、external dependencies、config/cache、runbook 和 questions。
5. 基于每个仓库 wiki 和源码/IDL，生成 `system/wiki/`。
6. `system/wiki/` 只记录跨服务事实，不复制下游服务内部实现；内部细节链接到 `repos/<repo-name>/wiki/`。
7. `.kb-cache/` 可用于 clone 或缓存输入 repo，但不应提交。

## System Wiki（跨仓库层）

优先生成：

- `service-catalog.md`：服务、repo、role、owner、wiki、runtime。
- `dependency-graph.md`：upstream、downstream、protocol、contract、failure impact。
- `contracts/`：IDL/source contract、producer/consumer、兼容性说明。
- `request-flows/`：端到端请求链路和 service hops。
- `runbooks/`：跨服务排障手册。
- `questions/`：缺失的 IDL、owner、dashboard、alert、日志样例。

## Ingest（吸收变更）

1. 明确目标范围：文件、模块、diff、PR、issue、设计文档、IDL/source contract 或用户提供材料。
2. 阅读原始源码/契约/材料。
3. 更新最小相关页面。
4. 在 frontmatter 中引用 `source_files`；兼容旧页时可保留 `related_files`。
5. 从 `index.md` 链接新页面。
6. 在 `log.md` 追加记录。

不要把大段代码复制进 wiki。优先写可验证总结、文件引用和跨页面链接。

## Query（回答并沉淀）

1. 阅读相关层级的 `index.md`。
2. 阅读候选页面。
3. 对强结论，打开相关源码、IDL/source contract 或 repo wiki 核验。
4. 如果 wiki 和代码冲突，信代码；当用户要求维护 wiki 时，同步修 wiki。
5. 有长期价值的问题答案写入 `queries/`。

## Refresh After Diff（按 diff 刷新）

1. 运行 `python3 <skill>/scripts/changed_files.py --wiki wiki` 或指定 `repos/<repo>/wiki`。
2. 检查受影响页面的相关源码和附近测试。
3. 如果行为、职责、接口或依赖变化，更新页面。
4. 如果变更影响跨服务 contract、dependency graph 或 request flow，更新 `system/wiki/`。
5. 运行 `wiki_lint.py`。

## Deepen（深化）

1. 把 endpoint summary 升级成 API reference，包含 route、method、handler、request fields、field source、requiredness、response shape、error behavior、IDL source 和 examples。
2. 在最终确认 API 字段前搜索 source IDL。参考 `references/accuracy-and-runtime.md`；如果 source IDL 不在仓库内，更新 question 页面并记录搜索命令和证据。
3. 为影响运行时行为的 RPC、cache、config service、queue、object storage 或 collector 补 external dependency 页面。
4. 补 config/cache 运行细节：JSON shape、defaults、test-only flags、runtime impact、reload behavior、cache key shape、TTL 和 invalidation path。
5. 为最可能的事故或接口失败补 runbook，包括 owners、metrics dashboards、alerts 和 common error log samples。如果仓库或用户上下文中没有这些信息，创建 question 页面，不要猜。
6. 把有噪音但有历史价值的 log entry 标记为 superseded，不要直接删除。

## First Pass Content Standard（首轮内容标准）

不要把首轮 wiki 做成只有标题的空壳。即使信息不完整，也应该从源码提取下面这些可验证内容：

- 路由、handler、middleware、client、配置 getter、cache key、metrics key 和日志前缀。
- 每个核心 endpoint 的字段来源、必填性、响应结构和错误行为。
- 每个外部依赖的调用方源码、hard/degradable 分类、失败传播和用户可见影响。
- 每条核心 flow 的执行序列、身份来源、上下文写入、状态副作用和失败模式。
- 运维元信息如果缺失，要写入 `questions/operations-metadata.md`，并区分“代码中确认的 metrics/logs”和“线上 dashboard/alert 待确认”。
