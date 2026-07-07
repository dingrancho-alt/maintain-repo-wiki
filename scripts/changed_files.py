#!/usr/bin/env python3
"""Map changed repository files to wiki pages that cite them."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from repo_wiki_common import iter_content_pages, parse_frontmatter, posix_rel, source_refs


def git_changed_files(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff failed")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def map_changed_files(wiki_dir: Path, changed_files: list[str]) -> dict:
    changed_set = set(changed_files)
    affected_pages = []
    mapped_files = set()

    for page in iter_content_pages(wiki_dir):
        meta, _body = parse_frontmatter(page)
        sources = set(source_refs(meta))
        if sources & changed_set:
            affected_pages.append(posix_rel(page, wiki_dir))
            mapped_files.update(sources & changed_set)

    return {
        "changed_files": changed_files,
        "affected_pages": sorted(affected_pages),
        "unmapped_changed_files": [path for path in changed_files if path not in mapped_files],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Find wiki pages affected by changed source files.")
    parser.add_argument("--wiki", default="wiki", help="Path to repo wiki directory")
    parser.add_argument("--repo-root", default=".", help="Repository root for git diff fallback")
    parser.add_argument("--changed", nargs="*", help="Changed files relative to repo root")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki).resolve()
    if not wiki_dir.exists():
        print(json.dumps({"error": f"wiki directory not found: {wiki_dir}"}, indent=2))
        return 1

    changed = args.changed if args.changed is not None else git_changed_files(Path(args.repo_root).resolve())
    print(json.dumps(map_changed_files(wiki_dir, changed), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
