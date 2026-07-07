#!/usr/bin/env python3
"""Shared helpers for repo wiki scripts."""

from __future__ import annotations

import re
from pathlib import Path


CORE_FILES = {
    "index.md",
    "log.md",
    "source-map.md",
    "SCHEMA.md",
    "schema.md",
    "overview.md",
    "service-catalog.md",
    "dependency-graph.md",
}


def posix_rel(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def discover_repo_root(wiki_dir: Path) -> Path:
    wiki_dir = wiki_dir.resolve()
    if wiki_dir.name == "repo-wiki" and wiki_dir.parent.name == "docs":
        return wiki_dir.parent.parent
    if wiki_dir.name in {"wiki", "system-wiki"}:
        return wiki_dir.parent
    return Path.cwd().resolve()


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    if not text.startswith("---\n"):
        return {}, text

    end = text.find("\n---", 4)
    if end == -1:
        return {}, text

    raw = text[4:end]
    body = text[end + len("\n---") :].lstrip("\n")
    return parse_simple_yaml(raw), body


def parse_simple_yaml(raw: str) -> dict:
    data: dict[str, object] = {}
    current_key: str | None = None

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("- ") and current_key:
            data.setdefault(current_key, [])
            value = stripped[2:].strip()
            if isinstance(data[current_key], list):
                data[current_key].append(unquote(value))
            continue

        if line[:1].isspace():
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key

        if not value:
            data[key] = []
        elif value.startswith("[") and value.endswith("]"):
            items = [item.strip() for item in value[1:-1].split(",") if item.strip()]
            data[key] = [unquote(item) for item in items]
        else:
            data[key] = unquote(value)

    return data


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def list_value(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        return [value]
    return []


def iter_wiki_pages(wiki_dir: Path) -> list[Path]:
    return sorted(path for path in wiki_dir.rglob("*.md") if path.is_file())


def iter_content_pages(wiki_dir: Path) -> list[Path]:
    return [path for path in iter_wiki_pages(wiki_dir) if path.name not in CORE_FILES]


def extract_markdown_links(text: str) -> list[str]:
    links = []
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).strip()
        if should_check_link(target):
            links.append(target.split("#", 1)[0])
    return links


def should_check_link(target: str) -> bool:
    lowered = target.lower()
    return not (
        lowered.startswith("http://")
        or lowered.startswith("https://")
        or lowered.startswith("mailto:")
        or lowered.startswith("#")
        or not target
    )


def load_index_links(wiki_dir: Path) -> set[str]:
    index = wiki_dir / "index.md"
    if not index.exists():
        return set()
    links = set()
    for link in extract_markdown_links(index.read_text()):
        links.add(Path(link).as_posix())
    return links


def page_record(path: Path, wiki_dir: Path) -> dict:
    meta, _body = parse_frontmatter(path)
    related = source_refs(meta)
    return {
        "path": posix_rel(path, wiki_dir),
        "title": str(meta.get("title", path.stem.replace("-", " ").title())),
        "type": str(meta.get("type", "")),
        "status": str(meta.get("status", "")),
        "source_files": related,
        "related_files": related,
        "tags": list_value(meta.get("tags")),
    }


def source_refs(meta: dict) -> list[str]:
    refs = []
    seen = set()
    for key in ("source_files", "related_files"):
        for value in list_value(meta.get(key)):
            if value not in seen:
                refs.append(value)
                seen.add(value)
    return refs
