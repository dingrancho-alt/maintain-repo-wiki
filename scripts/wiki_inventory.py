#!/usr/bin/env python3
"""Emit repo wiki page metadata as JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from repo_wiki_common import iter_content_pages, page_record, parse_frontmatter


def build_inventory(wiki_dir: Path) -> dict:
    pages = []
    for path in iter_content_pages(wiki_dir):
        meta, _body = parse_frontmatter(path)
        if meta:
            pages.append(page_record(path, wiki_dir))
    return {"wiki": str(wiki_dir), "page_count": len(pages), "pages": pages}


def main() -> int:
    parser = argparse.ArgumentParser(description="List repo wiki pages and source references.")
    parser.add_argument("wiki", nargs="?", default="wiki", help="Path to repo wiki directory")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki).resolve()
    if not wiki_dir.exists():
        print(json.dumps({"error": f"wiki directory not found: {wiki_dir}"}, indent=2))
        return 1

    print(json.dumps(build_inventory(wiki_dir), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
