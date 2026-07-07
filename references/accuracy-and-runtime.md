# 准确性与运行时信息补充

当第一版 wiki 需要更可信的 API 信息，或需要更真实地反映运行时行为时，使用本参考。

## 定位源 IDL / Source Contract

在最终确认 API 字段前先搜索契约来源：

```bash
rg --files -g '*.thrift' -g '*.proto' -g '*.idl' -g '*openapi*' -g '*swagger*'
rg -n "idl|thrift|proto|openapi|swagger|kitex|hertz|generate|gen" .
```

同时检查 build 文件、生成脚本、`go:generate` 注释、CI 配置、`go.mod`、`.gitmodules`、README/deploy 文档，以及 generated code header。

找到来源后，更新 API 页面：

- `## IDL Source（IDL 来源）`：记录路径、生成器、生成产物路径和最近验证 commit。
- endpoint 字段表：记录字段名、来源、必填性、类型、默认值、校验逻辑和响应结构。

找不到来源时，更新或创建 `questions/idl-source-location.md`，记录：

- 执行过的搜索命令；
- 检查过的路径；
- 可能的外部仓库或包线索；
- 仍未验证的字段。

不要只根据 handler 名称推断缺失字段。定位 IDL/source contract 的目的，是让生成的 API 信息准确可信。

## 反映真实运行时

写 business flow、field propagation、runbook 或运行时页面前，先搜索仓库文档、部署/配置文件、监控元信息和测试 fixture：

```bash
rg -n "owner|oncall|dashboard|grafana|argos|metrics|alarm|alert|报警|日志|log|SLO|SLA" .
```

只有能从仓库文件、监控配置、部署元信息或用户提供上下文中确认时，才写入 runbook：

- 服务 owner 或 oncall group；
- metrics dashboard 名称或链接；
- alert 名称及触发含义；
- 常见错误日志样例；
- trace/debug 所需 request identifier；
- fast checks 和 mitigation steps。

如果无法确认，创建 `questions/operations-metadata.md`，列出缺失的 owner、dashboard、alert、log source，并向用户询问这些信息从哪里获取。不要编造运维信息，因为目标是反映真实运行时。

## 业务流程与字段传播

当用户问“某字段是否传给下游”“某业务策略在哪里生效”“为什么线上表现和请求参数不一致”时，优先补 `flows/field-propagation.md` 和具体业务 flow：

- 从 API/IDL 字段开始，记录字段来源、必填性、默认值和校验。
- 沿 handler/adapter/request builder/provider/filter/packer/recorder 追踪字段。
- 对每个下游 RPC/event/cache/search/sort 请求，记录字段是否传入、字段名是否变化、是否被配置映射或覆盖。
- 记录 metrics/logs 如何验证字段或阶段是否生效，例如 request id、metric name/tag、日志 pattern。
- 无法确认时写 `unknown` 和下一步检查，不要用“应该会透传”替代验证结论。
