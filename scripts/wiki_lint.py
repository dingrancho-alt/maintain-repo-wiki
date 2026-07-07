#!/usr/bin/env python3
"""Lint a repository wiki for stale or disconnected pages."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from repo_wiki_common import (
    CORE_FILES,
    discover_repo_root,
    extract_markdown_links,
    iter_wiki_pages,
    list_value,
    load_index_links,
    parse_frontmatter,
    posix_rel,
    source_refs,
)


REQUIRED_KEYS = {"title", "type", "status"}
UNCERTAIN_PATTERN = re.compile(r"\b(TODO|TBD|FIXME)\b", re.IGNORECASE)
FIELD_TABLE_PATTERN = re.compile(r"\|\s*Field\s*\|\s*Source\s*\|\s*Required\s*\|", re.IGNORECASE)
EXAMPLE_PATTERN = re.compile(r"Example Request|Example Response", re.IGNORECASE)
IDL_SOURCE_PATTERN = re.compile(r"##\s+IDL Source", re.IGNORECASE)
BUSINESS_CONTEXT_PATTERN = re.compile(r"##\s+Business Context", re.IGNORECASE)
FIELD_PROPAGATION_PATTERN = re.compile(r"##\s+Field Propagation", re.IGNORECASE)
FIELD_MATRIX_PATTERN = re.compile(r"##\s+Field Matrix", re.IGNORECASE)
DOWNSTREAM_MAPPING_PATTERN = re.compile(r"##\s+Downstream Request Mapping", re.IGNORECASE)
RUNTIME_OBSERVABILITY_PATTERN = re.compile(r"##\s+Runtime Observability", re.IGNORECASE)


@dataclass
class Issue:
    path: str
    message: str


def lint_wiki(wiki_dir: Path, quality: bool = False) -> list[Issue]:
    issues: list[Issue] = []
    repo_root = discover_repo_root(wiki_dir)

    if not wiki_dir.exists():
        return [Issue(str(wiki_dir), "wiki directory does not exist")]

    index_links = load_index_links(wiki_dir)
    if not (wiki_dir / "index.md").exists():
        issues.append(Issue("index.md", "index.md does not exist"))

    for path in iter_wiki_pages(wiki_dir):
        rel = posix_rel(path, wiki_dir)
        text = path.read_text()
        meta, body = parse_frontmatter(path)

        for link in extract_markdown_links(text):
            target = (path.parent / link).resolve()
            if not target.exists():
                issues.append(Issue(rel, f"markdown link target does not exist: {link}"))

        if UNCERTAIN_PATTERN.search(body):
            issues.append(Issue(rel, "contains TODO/TBD/FIXME marker"))

        if path.name in CORE_FILES:
            continue

        if not meta:
            issues.append(Issue(rel, "missing YAML frontmatter"))
            continue

        missing = sorted(REQUIRED_KEYS - set(meta))
        if missing:
            issues.append(Issue(rel, f"missing frontmatter key(s): {', '.join(missing)}"))

        if rel not in index_links:
            issues.append(Issue(rel, "page is not linked from index.md"))

        for source in source_refs(meta):
            if not (repo_root / source).exists():
                issues.append(Issue(rel, f"source file does not exist: {source}"))

        if quality:
            issues.extend(lint_quality(rel, meta, body))

    return issues


def lint_quality(rel: str, meta: dict, body: str) -> list[Issue]:
    issues: list[Issue] = []
    page_type = str(meta.get("type", "")).lower()
    haystack = " ".join(
        [
            rel.lower(),
            str(meta.get("title", "")).lower(),
            " ".join(list_value(meta.get("tags"))).lower(),
            body.lower(),
        ]
    )
    labels = " ".join(
        [
            rel.lower(),
            str(meta.get("title", "")).lower(),
            " ".join(list_value(meta.get("tags"))).lower(),
        ]
    )

    if page_type == "api":
        if not IDL_SOURCE_PATTERN.search(body):
            issues.append(Issue(rel, "API reference is missing IDL source section"))
        if not FIELD_TABLE_PATTERN.search(body):
            issues.append(Issue(rel, "API reference is missing endpoint field table"))
        if not EXAMPLE_PATTERN.search(body):
            issues.append(Issue(rel, "API reference is missing request/response examples"))
        if "## Errors" not in body and "## Error" not in body:
            issues.append(Issue(rel, "API reference is missing error behavior section"))

    if "external-dependencies" in labels or "dependency" in labels:
        if "## Failure Impact" not in body:
            issues.append(Issue(rel, "dependency page is missing failure impact section"))
        if "## Dependency Matrix" not in body:
            issues.append(Issue(rel, "dependency page is missing dependency matrix"))

    if "config" in labels or "cache" in labels:
        if "## Defaults" not in body:
            issues.append(Issue(rel, "configuration page is missing defaults section"))
        if "## Runtime Impact" not in body:
            issues.append(Issue(rel, "configuration page is missing runtime impact section"))

    if "auth" in labels or "identity" in labels:
        if "## Identity Sources" not in body:
            issues.append(Issue(rel, "auth/identity page is missing identity sources section"))

    if "business-flow" in labels or "business flow" in labels:
        if not BUSINESS_CONTEXT_PATTERN.search(body):
            issues.append(Issue(rel, "business flow page is missing business context section"))
        if not RUNTIME_OBSERVABILITY_PATTERN.search(body):
            issues.append(Issue(rel, "business flow page is missing runtime observability section"))

    if "field-propagation" in labels or "field propagation" in labels:
        if not FIELD_MATRIX_PATTERN.search(body):
            issues.append(Issue(rel, "field propagation page is missing field matrix section"))
        if not DOWNSTREAM_MAPPING_PATTERN.search(body):
            issues.append(Issue(rel, "field propagation page is missing downstream request mapping section"))
        if "## Config And Defaults" not in body:
            issues.append(Issue(rel, "field propagation page is missing config and defaults section"))
        if "## Observability" not in body and not RUNTIME_OBSERVABILITY_PATTERN.search(body):
            issues.append(Issue(rel, "field propagation page is missing observability section"))

    if page_type == "flow" and ("runtime-observability" in labels or "observability" in labels):
        if "## Runtime Signals" not in body:
            issues.append(Issue(rel, "runtime observability page is missing runtime signals section"))
        if "## Request Correlation" not in body:
            issues.append(Issue(rel, "runtime observability page is missing request correlation section"))
        if "## Flow To Signal Map" not in body:
            issues.append(Issue(rel, "runtime observability page is missing flow to signal map section"))

    if page_type == "runbook":
        if "## Owners" not in body:
            issues.append(Issue(rel, "runbook is missing owners section"))
        if "## Metrics Dashboards" not in body:
            issues.append(Issue(rel, "runbook is missing metrics dashboards section"))
        if "## Alerts" not in body:
            issues.append(Issue(rel, "runbook is missing alerts section"))
        if "## Common Error Logs" not in body:
            issues.append(Issue(rel, "runbook is missing common error logs section"))

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint a repository wiki.")
    parser.add_argument("wiki", nargs="?", default="wiki", help="Path to repo wiki directory")
    parser.add_argument("--quality", action="store_true", help="Check API, dependency, config, and auth depth")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki).resolve()
    issues = lint_wiki(wiki_dir, quality=args.quality)
    print(f"{len(issues)} issue(s)")
    for issue in issues:
        print(f"- {issue.path}: {issue.message}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
