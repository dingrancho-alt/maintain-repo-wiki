# maintain-repo-wiki
单仓库/多仓库生产级LLM WIKI，具有自进化能力，业务资讯、问题排查、认知拓展。


`maintain-repo-wiki` 用于为代码仓库、微服务系统或集中式知识库仓库构建可长期维护的 Markdown 知识库。

它不是简单生成 README 或目录索引，而是把源码、IDL/source contract、配置、依赖、业务流程、字段传播、metrics/logs/alerts、排障经验和长期问答沉淀成一套工程知识库。目标是让 wiki 能回答新人理解、接口对接、业务咨询、历史背景、变更影响和线上排障问题。

## 适用场景

- 为单个仓库补齐 `wiki/`，让后来的人能快速理解架构、入口、模块边界和核心流程。
- 为多个仓库建立集中式知识库，把每个仓库事实和跨服务系统事实分开维护。
- 对已有 wiki 做深化，从“能入门”升级到“能支持接口对接、变更评估和排障”。
- 在代码变更、PR、IDL 变更或线上问题后，刷新相关 wiki 页面。
- 把反复被问到的业务问题沉淀为可复用 answers，避免同类问题每次重新分析。

## Agent 使用示例

把下面提示词发给支持 skill 的 agent 即可。运行方式和质量要求由 `SKILL.md` 定义，不需要在提示词里重复。

### 初始化

```text
使用 maintain-repo-wiki，给以下仓库初始化并填充一版工程知识库。仓库1：xxx；仓库2：xxx（可以是本地绝对路径、也可以是github链接）
```

### 注入

```text
使用 maintain-repo-wiki，把下面这次代码变更/设计文档/排障结论注入当前仓库 wiki：

<贴 diff、PR 链接、设计文档、日志结论或变更说明>
```

### 查询

```text
使用 maintain-repo-wiki，基于当前仓库 wiki 回答这个问题：

<写具体业务咨询、字段传播、接口对接、变更影响或排障问题>
```

## 核心原则

- 以源码、IDL/source contract、仓库文档、配置、日志和用户提供事实为准，不靠猜。
- 从面到点组织知识：先系统架构和服务边界，再源码地图、业务流程、字段传播、API、配置缓存和 runbook。
- Flow 不只写认证链路；核心业务入口都应该有业务流程、字段来源、状态副作用、失败模式和验证方式。
- 不复制完整源码，只记录可验证结论、源码引用、接口契约、运行时关系和未决问题。
- 不确定的信息写入 `questions/`，不要伪装成结论。
- 新增或明显修改页面时，同步更新 `index.md` 和 `log.md`。

## 三种模式

### Repo Mode

用于单仓库自己的知识库，默认生成 `wiki/`。

```bash
python3 /Users/bytedance/.codex/skills/maintain-repo-wiki/scripts/init_repo_wiki.py <repo-root>
```

典型输出：

```text
wiki/
├── index.md
├── log.md
├── SCHEMA.md
├── overview.md
├── source-map.md
├── components/
├── flows/
├── apis/
├── runbooks/
├── queries/
├── questions/
└── decisions/
```

### System Mode

用于维护跨仓库、跨服务的全局知识，不保存每个仓库的完整 wiki。默认生成 `system-wiki/`。

```bash
python3 /Users/bytedance/.codex/skills/maintain-repo-wiki/scripts/init_repo_wiki.py <root> --mode system
```

适合记录 service catalog、dependency graph、cross-service request flow、field flow、contracts 和跨服务 runbook。

### Knowledge Repo Mode

用于新建专门的知识库仓库，同时保存多个输入仓库的独立 wiki 和全局系统 wiki。

```bash
python3 /Users/bytedance/.codex/skills/maintain-repo-wiki/scripts/init_repo_wiki.py <knowledge-repo-root> --mode knowledge \
  --repo https://code.byted.org/mercury/oversea_open_stream \
  --repo /abs/path/to/local/repo
```

典型输出：

```text
knowledge-repo/
├── sources.yaml
├── repos/
│   └── <repo-name>/wiki/
└── system/
    └── wiki/
```

## 推荐工作流

### 1. Bootstrap

初始化 wiki 后，先读真实仓库上下文：

```bash
rg --files
```

优先检查 README、AGENTS/CLAUDE 文档、package/build config、服务入口、路由定义、配置、IDL/source contract 和测试。首批页面优先填实：

- `overview.md`
- `source-map.md`
- `components/config-and-cache.md`
- `components/external-dependencies.md`
- `flows/auth-and-identity.md`
- `flows/business-flows.md`
- `flows/field-propagation.md`
- `flows/runtime-observability.md`
- 主要 `apis/`
- 最高风险 `runbooks/`

### 2. Ingest

吸收代码、diff、PR、issue、设计文档或 IDL/source contract 时：

- 先读原始材料，再写 wiki。
- 只更新最小相关页面。
- 在 frontmatter 中用 `source_files` 记录源码引用。
- 集中式知识库还应记录 `repo`、`repo_url`、`verified_commit`。
- 有长期价值的问答写入 `queries/`。

### 3. Deepen

当 wiki 只能入门但还不能支撑排障或变更评估时，继续补：

- API 字段表、字段来源、必填性、响应结构、错误行为和示例。
- Business flow、field propagation、外部依赖失败影响、配置缓存 runtime impact。
- metrics name/tag、log pattern、request id、dashboard、alert、owner 和 common error logs。
- 找不到的 contract、owner、dashboard、alert 或日志入口，写入 `questions/` 并记录搜索证据。

### 4. Query

回答问题时先读当前 wiki 的 `index.md`，再按问题类型跳转：

- 单仓库问题：读 `wiki/` 或 `repos/<repo>/wiki/`。
- 跨服务问题：先读 `system/wiki/`，再跳到具体仓库 wiki 和源码。
- 字段/流程问题：优先读 `flows/field-propagation.md`、相关业务 flow、API 字段表、config/cache 和 runbook。

如果 wiki 无法回答，补齐对应页面或新增 `queries/<question>.md`，让下次不用重来。

### 5. Refresh

代码变更后，用 changed-files 工具定位受影响页面：

```bash
python3 /Users/bytedance/.codex/skills/maintain-repo-wiki/scripts/changed_files.py --wiki wiki
```

也可以显式传入变更文件：

```bash
python3 /Users/bytedance/.codex/skills/maintain-repo-wiki/scripts/changed_files.py \
  --wiki wiki \
  --changed biz/handler/foo.go biz/domain/bar.go
```

然后重新阅读受影响源码，刷新相关 wiki。若影响跨服务 contract、dependency graph 或 request flow，同步更新 `system/wiki/`。

## 质量检查

基础 lint：

```bash
python3 /Users/bytedance/.codex/skills/maintain-repo-wiki/scripts/wiki_lint.py wiki
```

质量 lint：

```bash
python3 /Users/bytedance/.codex/skills/maintain-repo-wiki/scripts/wiki_lint.py wiki --quality
```

`--quality` 会检查 API、依赖、配置、auth/identity、runbook 等页面是否足以支撑接口对接、运行时理解和排障。

输出页面元数据：

```bash
python3 /Users/bytedance/.codex/skills/maintain-repo-wiki/scripts/wiki_inventory.py wiki
```

## 页面应该写到什么深度

一个合格的工程 wiki 应能回答这些问题：

- 这个仓库负责什么，核心入口在哪里？
- 某个 HTTP/RPC/event 接口的 contract、字段来源、必填性、错误行为是什么？
- 某个业务字段从入口到下游依赖如何传播？在哪里被默认、改写、过滤或落库？
- 某个状态变化会产生哪些副作用？
- 依赖失败、超时、返回异常时，用户可见影响是什么？
- 出问题时看哪些 metrics、logs、alerts、dashboard 和 request id？
- 代码变更会影响哪些 flow、API、config/cache、runbook 或跨服务 contract？

如果 wiki 不能回答这些问题，就继续深化，而不是只保留目录级说明。

## 脚本速查

- `scripts/init_repo_wiki.py`：初始化 Repo/System/Knowledge Repo 三种模式。
- `scripts/wiki_lint.py`：检查 wiki 健康度和质量门槛。
- `scripts/changed_files.py`：把变更源码文件映射到引用它们的 wiki 页面。
- `scripts/wiki_inventory.py`：输出页面元数据 JSON，便于审计或自动化。

## 参考资料

- `SKILL.md`：完整行为规则和工作流。
- `references/lint-rules.md`：lint 和质量检查规则。
- `references/page-schemas.md`：页面 schema 和 frontmatter 约定。
- `references/quality-gates.md`：工程知识库质量门槛。
- `references/workflows.md`：更细的维护流程。
- `references/accuracy-and-runtime.md`：准确性和运行时证据要求。
