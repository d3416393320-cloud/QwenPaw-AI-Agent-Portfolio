# -*- coding: utf-8 -*-
"""Shared utilities for the B2B CLI."""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

MEMORY_DIR = Path("memory")
OUTPUT_DIR = Path("output")
REPORTS_DIR = Path("reports")


def ensure_project_dirs() -> None:
    for path in (MEMORY_DIR, OUTPUT_DIR, REPORTS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def slugify(value: str | None) -> str:
    text = (value or "customer").strip()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^0-9A-Za-z_\-\u4e00-\u9fff]+", "", text)
    return text or "customer"


def today_iso() -> str:
    return dt.date.today().isoformat()


def read_text_file(path: str | Path) -> str:
    file_path = Path(path)
    for encoding in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return file_path.read_text(encoding="utf-8", errors="replace")


def write_text_file(path: str | Path, text: str) -> Path:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(text, encoding="utf-8")
    return file_path


def write_json_file(path: str | Path, payload: dict[str, Any]) -> Path:
    return write_text_file(path, json.dumps(payload, ensure_ascii=False, indent=2))


def load_json_file(path: str | Path) -> dict[str, Any]:
    return json.loads(read_text_file(path))


def memory_path(customer: str, prefix: str, ext: str = "json", dated: bool = False) -> Path:
    ensure_project_dirs()
    suffix = f"_{today_iso()}" if dated else ""
    return MEMORY_DIR / f"{prefix}_{slugify(customer)}{suffix}.{ext}"


def latest_customer_json(customer: str) -> Path:
    ensure_project_dirs()
    slug = slugify(customer)
    stable = MEMORY_DIR / f"customer_{slug}.json"
    if stable.exists():
        return stable
    candidates = sorted(MEMORY_DIR.glob(f"customer_{slug}_*.json"), reverse=True)
    if candidates:
        return candidates[0]
    raise FileNotFoundError(f"customer memory not found: {stable}")


def latest_backcheck_file(customer: str) -> Path | None:
    ensure_project_dirs()
    slug = slugify(customer)
    patterns = [f"backcheck_{slug}*.txt", f"背调_{slug}*.txt", f"backcheck_{slug}*.json"]
    candidates: list[Path] = []
    for pattern in patterns:
        candidates.extend(MEMORY_DIR.glob(pattern))
    return sorted(candidates, reverse=True)[0] if candidates else None


def normalize_lines(text: str) -> list[str]:
    return [re.sub(r"\s+", " ", line).strip(" \t:-：|│") for line in text.splitlines() if line.strip()]


def truncate_text(text: str, max_chars: int, marker: str = "\n...[truncated]...\n") -> str:
    text = text.strip()
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    keep = max_chars - len(marker)
    if keep <= 0:
        return text[:max_chars]
    head = int(keep * 0.7)
    tail = keep - head
    return text[:head].rstrip() + marker + text[-tail:].lstrip()


def print_stderr(message: str, quiet: bool = False) -> None:
    if not quiet:
        print(message, file=sys.stderr)
