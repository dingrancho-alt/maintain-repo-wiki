#!/usr/bin/env python3
"""Initialize engineering-manual style repo and system wikis."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


REPO_DIRECTORIES = ["components", "flows", "apis", "runbooks", "queries", "questions", "decisions"]
SYSTEM_DIRECTORIES = ["repos", "contracts", "request-flows", "field-flows", "runbooks", "questions"]


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return True


def index_template() -> str:
    return """# 仓库知识库

这是当前仓库的持久化工程知识库入口。首轮维护目标不是只生成目录，而是基于源码、IDL/source contract、配置和运行时线索，沉淀可用于接口对接、变更评审、依赖影响判断和常见故障排查的知识。

## 语言策略

wiki 正文以中文为主要语言。代码标识符、文件路径、API 字段名、配置 key、日志字段、metrics、alert、服务名、错误码和精确运行时字面量保留原文。

## 核心地图

- [仓库概览](overview.md)
- [源码地图](source-map.md)
- [Schema](SCHEMA.md)
- [维护日志](log.md)

## 组件

- [配置与缓存运行时](components/config-and-cache.md)
- [外部依赖与失败影响](components/external-dependencies.md)

## 流程

- [认证与身份流程](flows/auth-and-identity.md)
- [业务流程索引](flows/business-flows.md)
- [字段传播矩阵](flows/field-propagation.md)
- [运行时观测](flows/runtime-observability.md)

## API

- [HTTP Endpoints](apis/http-endpoints.md)

## Runbooks

- [请求排障手册](runbooks/request-troubleshooting.md)

## 未决问题

- [IDL 源文件位置](questions/idl-source-location.md)
- [运行元数据来源](questions/operations-metadata.md)

## 持续沉淀

- `queries/`：值得长期保留的问题答案和分析。
- `decisions/`：架构决策和取舍。
"""


def schema_template() -> str:
    return """# Repo Wiki Schema

每个非核心页面都应该以 frontmatter 开头：

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

`related_files` 作为兼容字段仍可被脚本识别；新页面优先使用 `source_files`，因为它更直接表达“这些结论来自哪些源码文件”。

正文默认使用中文；代码符号、路径、API 字段、配置 key、日志字段、metrics、alert、服务名和错误码保留英文原文。

## 页面类型

- `component`：模块、handler、client、配置对象、缓存、外部依赖。
- `flow`：业务流程、字段传播、请求链路、认证身份、数据流、状态变化、失败路径、运行时可观测性。
- `api`：endpoint/interface 级别接口手册。
- `runbook`：现象、owner、dashboard、alert、日志、快速检查、缓解和升级路径。
- `question`：无法从源码或运行时确认的信息，记录搜索证据和下一步。
- `query`：值得长期保留的问题答案。
- `decision`：架构背景、决策、影响、备选方案和重新评估触发条件。

保持结论可验证，引用 source files，并在验证后更新元数据。
"""


def overview_template() -> str:
    return """---
title: 仓库概览
type: overview
status: draft
source_files: []
last_verified_commit: unknown
last_verified: YYYY-MM-DD
tags:
  - overview
---

# 仓库概览

用本页说明仓库的技术栈、核心职责、目录地图、关键入口和主要架构关系。首轮填写时只写能从源码、配置、README、IDL 或用户上下文确认的信息。

## Tech Stack

## Responsibilities

## Directory Map

## Entrypoints

## Architecture

## Runtime Notes

## Key Pages
"""


def log_template() -> str:
    today = date.today().isoformat()
    return f"""# Repo Wiki Log

- {today}: 初始化 repo wiki。
"""


def source_map_template() -> str:
    return """# Source Map

记录高层源码区域和对应的主要 wiki 页面。

| Source path | Wiki page | Notes |
| --- | --- | --- |
"""


def api_template() -> str:
    return """---
title: HTTP Endpoints
type: api
status: draft
source_files: []
last_verified_commit: unknown
last_verified: YYYY-MM-DD
tags:
  - http
  - api
---

# HTTP Endpoints

## Surface

| Endpoint | Method | Handler | Purpose |
| --- | --- | --- | --- |

## IDL Source

记录源 IDL/source contract、生成入口和生成产物。找不到时，把搜索证据写入 `questions/idl-source-location.md`。

| Source | Path Or Link | Notes |
| --- | --- | --- |

## Endpoint Reference

为每个 endpoint 建独立小节，字段表需要说明来源、必填性和类型。

### Endpoint Name

| Field | Source | Required | Type | Description |
| --- | --- | --- | --- | --- |

## Identity Sources

| Source | Field/Context | Used By | Notes |
| --- | --- | --- | --- |

## Example Request

```bash
curl '<url>'
```

## Example Response

```json
{}
```

## Errors And Status Codes

## Callers
"""


def config_cache_template() -> str:
    return """---
title: 配置与缓存运行时
type: component
status: draft
source_files: []
last_verified_commit: unknown
last_verified: YYYY-MM-DD
tags:
  - config
  - cache
---

# 配置与缓存运行时

## Responsibility

## Config Sources

| Config | Source | Reader | Runtime Impact |
| --- | --- | --- | --- |

## JSON Shapes

```json
{}
```

## Defaults

| Config | Default | Source | Notes |
| --- | --- | --- | --- |

## Runtime Impact

## Cache Keys And TTL

| Cache | Key Shape | TTL | Invalidation |
| --- | --- | --- | --- |

## Test Or Lane Behavior

## Failure Modes
"""


def external_dependencies_template() -> str:
    return """---
title: 外部依赖与失败影响
type: component
status: draft
source_files: []
last_verified_commit: unknown
last_verified: YYYY-MM-DD
tags:
  - external-dependencies
  - dependencies
---

# 外部依赖与失败影响

## Responsibility

本页集中说明当前仓库访问的外部服务、配置中心、缓存、消息队列、对象存储、metrics 和 shared library，以及失败时在本服务中的传播方式和用户可见影响。

## Dependency Matrix

| Dependency | Kind | Client/Source Files | Hard Or Degradable | Timeout/Error Handling | User-Visible Impact |
| --- | --- | --- | --- | --- | --- |

## Failure Impact

## Fallbacks And Degradation

## Logs And Metrics

## Owners And Escalation

## Change Notes
"""


def auth_identity_template() -> str:
    return """---
title: 认证与身份流程
type: flow
status: draft
source_files: []
last_verified_commit: unknown
last_verified: YYYY-MM-DD
tags:
  - auth
  - identity
---

# 认证与身份流程

## Entry Points

## Middleware Or Handler Sequence

## Identity Sources

| Source | Field/Context | Used By | Failure Signal |
| --- | --- | --- | --- |

## Tenant And Partner Resolution

## Token Or User Resolution

## Region Or Runtime Context

## Failure Modes

## Verification Notes
"""


def business_flows_template() -> str:
    return """---
title: 业务流程索引
type: flow
status: draft
source_files: []
last_verified_commit: unknown
last_verified: YYYY-MM-DD
tags:
  - business-flow
---

# 业务流程索引

本页从业务问题出发组织流程，而不是只按代码模块组织。目标是让 wiki 能回答“某个请求、字段、状态或策略在业务上怎么工作”。

## Business Context

| Business Question | Flow Page | Main Entry | Runtime Evidence |
| --- | --- | --- | --- |

## Core Flows

| Flow | Entry Point | Main Components | Downstream Dependencies | State Side Effects |
| --- | --- | --- | --- | --- |

## Field Hotspots

| Field Or State | Why It Matters | Source | Downstream Use | Details |
| --- | --- | --- | --- | --- |

## Runtime Observability

| Flow | Metrics | Logs | Alerts | Dashboard |
| --- | --- | --- | --- | --- |

## Open Questions
"""


def field_propagation_template() -> str:
    return """---
title: 字段传播矩阵
type: flow
status: draft
source_files: []
last_verified_commit: unknown
last_verified: YYYY-MM-DD
tags:
  - field-propagation
---

# 字段传播矩阵

本页按关键字段组织，回答字段从入口到下游依赖、缓存、事件、响应的传播路径。

## Scope

说明覆盖的接口、RPC、event、cache 或业务流程。

## Field Matrix

| Field | Source | Validation Or Mapping | Internal Object | Downstream | Runtime Use | Missing Or Error Behavior |
| --- | --- | --- | --- | --- | --- | --- |

## Downstream Request Mapping

| Downstream | Request Builder | Source Fields | Renamed Fields | Dropped Or Defaulted Fields | Evidence |
| --- | --- | --- | --- | --- | --- |

## Config And Defaults

| Field | Config | Default | Runtime Impact |
| --- | --- | --- | --- |

## Observability

| Field Or Stage | Metric | Log Pattern | Dashboard/Alert | How To Check |
| --- | --- | --- | --- | --- |

## Open Questions
"""


def runtime_observability_template() -> str:
    return """---
title: 运行时观测
type: flow
status: draft
source_files: []
last_verified_commit: unknown
last_verified: YYYY-MM-DD
tags:
  - runtime
  - observability
---

# 运行时观测

本页把业务流程与 metrics、logs、alerts、dashboard 和 request id 连接起来，用于回答线上表现和排障问题。

## Business Context

| Flow Or Feature | Why It Matters | Primary Symptoms |
| --- | --- | --- |

## Runtime Signals

| Signal | Metric/Log/Alert | Source | Tags Or Fields | Meaning |
| --- | --- | --- | --- | --- |

## Request Correlation

| Identifier | Source | Propagates To | How To Search |
| --- | --- | --- | --- |

## Flow To Signal Map

| Flow Stage | Expected Metric | Key Logs | Failure Signal | First Check |
| --- | --- | --- | --- | --- |

## Dashboards And Alerts

| Dashboard/Alert | Scope | Owner | Link Or Source |
| --- | --- | --- | --- |

## Open Questions
"""


def runbook_template() -> str:
    return """---
title: 请求排障手册
type: runbook
status: draft
source_files: []
last_verified_commit: unknown
last_verified: YYYY-MM-DD
tags:
  - runbook
  - troubleshooting
---

# 请求排障手册

## Symptoms

## Owners

无法从仓库确认 owner 时，记录到 `questions/operations-metadata.md`，不要猜。

## Fast Checks

## Metrics Dashboards

## Alerts

## Common Error Logs

## Identity Sources

| Source | Field/Context | Fast Check | Failure Signal |
| --- | --- | --- | --- |

## Defaults

## Runtime Impact

## Mitigations

## Escalation
"""


def idl_question_template() -> str:
    return """---
title: IDL 源文件位置
type: question
status: draft
source_files: []
last_verified_commit: unknown
last_verified: YYYY-MM-DD
tags:
  - idl
  - contract
---

# IDL 源文件位置

## Question

当前仓库使用的源 IDL/source contract 在哪里维护，生成流程是什么，哪些生成文件必须与它保持一致？

## Search Evidence

| Checked Path Or Command | Result | Notes |
| --- | --- | --- |

## Current Best Answer

## Next Checks
"""


def operations_question_template() -> str:
    return """---
title: 运行元数据来源
type: question
status: draft
source_files: []
last_verified_commit: unknown
last_verified: YYYY-MM-DD
tags:
  - operations
  - runtime
---

# 运行元数据来源

## Question

服务 owner、oncall、metrics dashboard、alert 名称、日志检索入口和常见错误样例分别从哪里确认？

## Search Evidence

| Checked Source | Result | Notes |
| --- | --- | --- |

## Confirmed Runtime Metadata

| Item | Value | Source |
| --- | --- | --- |

## Next Checks
"""


def system_index_template() -> str:
    return """# System Wiki

使用本页作为跨仓库微服务知识库的入口。

## Core Maps（核心索引）

- [Service Catalog](service-catalog.md)
- [Dependency Graph](dependency-graph.md)
- [Maintenance Log](log.md)

## Knowledge Areas（知识区域）

- `repos/`：每个仓库的摘要和本地 wiki 链接。
- `contracts/`：跨服务接口契约、IDL/source contract、producer/consumer。
- `request-flows/`：端到端请求链路。
- `field-flows/`：跨服务关键字段传播。
- `runbooks/`：跨服务排障手册。
- `questions/`：跨仓库无法确认的信息。
"""


def service_catalog_template() -> str:
    return """# Service Catalog

| Service | Repo | Role | Owner | Wiki | Runtime |
| --- | --- | --- | --- | --- | --- |
"""


def dependency_graph_template() -> str:
    return """# Dependency Graph

| Upstream | Downstream | Protocol | Contract | Failure Impact |
| --- | --- | --- | --- | --- |

```mermaid
graph TD
  Pending["待从源码、IDL 和运行时信息确认服务依赖"]
```
"""


def repo_name_from_source(source: str) -> str:
    cleaned = source.rstrip("/")
    if "://" in cleaned:
        path = urlparse(cleaned).path.rstrip("/")
        name = Path(path).name
    else:
        name = Path(cleaned).name
    if name.endswith(".git"):
        name = name[:-4]
    return name.replace(" ", "-")


def source_type(source: str) -> str:
    return "git" if "://" in source or source.startswith("git@") else "local"


def sources_yaml_template(sources: list[str]) -> str:
    lines = [
        "# 输入仓库清单。source_type 支持 git 或 local。",
        "repos:",
    ]
    for source in sources:
        name = repo_name_from_source(source)
        kind = source_type(source)
        lines.extend(
            [
                f"  - name: {name}",
                f"    source_type: {kind}",
            ]
        )
        if kind == "git":
            lines.append(f"    url: {source}")
            lines.append("    branch: master")
        else:
            lines.append(f"    path: {source}")
        lines.extend(
            [
                "    role: 待确认",
                "    owner: 待确认",
                "    scan_mode: source_and_wiki",
            ]
        )
    return "\n".join(lines) + "\n"


def init_repo_wiki(repo_root: Path, wiki_path: str, mode: str) -> tuple[Path, list[str]]:
    wiki_dir = repo_root / wiki_path
    created = []

    directories = SYSTEM_DIRECTORIES if mode == "system" else REPO_DIRECTORIES
    for directory in directories:
        path = wiki_dir / directory
        path.mkdir(parents=True, exist_ok=True)
        created.append(path.relative_to(repo_root).as_posix() + "/")

    if mode == "system":
        files = {
            "index.md": system_index_template(),
            "service-catalog.md": service_catalog_template(),
            "dependency-graph.md": dependency_graph_template(),
            "log.md": log_template(),
        }
    else:
        files = {
            "index.md": index_template(),
            "SCHEMA.md": schema_template(),
            "overview.md": overview_template(),
            "log.md": log_template(),
            "source-map.md": source_map_template(),
            "apis/http-endpoints.md": api_template(),
            "components/config-and-cache.md": config_cache_template(),
            "components/external-dependencies.md": external_dependencies_template(),
            "flows/auth-and-identity.md": auth_identity_template(),
            "flows/business-flows.md": business_flows_template(),
            "flows/field-propagation.md": field_propagation_template(),
            "flows/runtime-observability.md": runtime_observability_template(),
            "runbooks/request-troubleshooting.md": runbook_template(),
            "questions/idl-source-location.md": idl_question_template(),
            "questions/operations-metadata.md": operations_question_template(),
        }

    for name, content in files.items():
        path = wiki_dir / name
        if write_if_missing(path, content):
            created.append(path.relative_to(repo_root).as_posix())

    return wiki_dir, created


def init_knowledge_repo(repo_root: Path, sources: list[str]) -> tuple[Path, list[str]]:
    created = []
    write_if_missing(repo_root / "sources.yaml", sources_yaml_template(sources))
    created.append("sources.yaml")

    for source in sources:
        name = repo_name_from_source(source)
        wiki_dir, child_created = init_repo_wiki(repo_root / "repos" / name, "wiki", "repo")
        created.extend([f"repos/{name}/{item}" for item in child_created])

    system_dir, system_created = init_repo_wiki(repo_root / "system", "wiki", "system")
    created.extend([f"system/{item}" for item in system_created])
    return system_dir, created


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a repository wiki, system wiki, or knowledge repo.")
    parser.add_argument("repo_root", nargs="?", default=".", help="Repository root directory")
    parser.add_argument("--mode", choices=["repo", "system", "knowledge"], default="repo", help="Wiki mode to initialize")
    parser.add_argument("--wiki-path", help="Wiki path relative to repo root")
    parser.add_argument("--repo", action="append", default=[], help="Input repo git URL or absolute local path for knowledge mode")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    repo_root.mkdir(parents=True, exist_ok=True)
    if args.mode == "knowledge":
        wiki_dir, created = init_knowledge_repo(repo_root, args.repo)
    else:
        wiki_path = args.wiki_path or ("system-wiki" if args.mode == "system" else "wiki")
        wiki_dir, created = init_repo_wiki(repo_root, wiki_path, args.mode)

    print(f"repo wiki: {wiki_dir}")
    print(f"created or confirmed {len(created)} path(s)")
    for item in created:
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
