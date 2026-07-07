# Lint 规则

`scripts/wiki_lint.py` 用于发现会降低 wiki 可信度的结构问题。它支持旧字段 `source_files`，也支持新字段 `related_files`。

当 wiki 需要支撑接口对接、运行时理解或排障时，使用 `--quality`：

```bash
python3 <skill>/scripts/wiki_lint.py wiki --quality
python3 <skill>/scripts/wiki_lint.py repos/<repo-name>/wiki --quality
```

## 必须修复的问题

- 缺少 `index.md`。
- 非核心页面缺少 frontmatter。
- frontmatter 缺少 `title`、`type` 或 `status`。
- 相对 Markdown 链接断裂。
- 页面未被 `index.md` 收录。
- `source_files` 或 `related_files` 指向的文件不存在。
- 页面正文残留 `TODO`、`TBD` 或 `FIXME`。

## 质量问题

这些问题只在 `--quality` 模式下检查：

- API 页面缺少 `Field | Source | Required` 字段表。
- API 页面缺少 `IDL Source` 小节。
- API 页面缺少请求或响应示例。
- API 页面缺少错误行为说明。
- 依赖页面缺少 dependency matrix 或 failure impact。
- 配置/缓存页面缺少 defaults 或 runtime impact。
- auth/identity 页面缺少 identity sources。
- 业务 flow 页面缺少 business context、field propagation、runtime observability 或 failure modes。
- 字段传播页面缺少字段矩阵、downstream mapping、config/defaults 或 observability。
- runbook 缺少 owners、metrics dashboards、alerts 或 common error logs。

## 可接受例外

- `questions/` 页面在调查未完成时可以使用 `status: draft`。
- 历史 `decisions/` 页面可以指向已经删除的源码文件，但需要使用 `status: retired`，并在正文说明源码为什么消失。
- 外部链接不会被 lint 脚本检查。
- `system/wiki/` 中的跨仓库页面可能没有直接 `related_files`，但必须能链接到 repo wiki、contract 或 question。

如果例外是有意保留的，在页面正文中说明原因，避免后续 agent 误修。
