# -*- coding: utf-8 -*-
"""Mailto and Gmail compose URL builders."""

from __future__ import annotations

import urllib.parse

DEFAULT_BODY_CHUNK_CHARS = 2000


def chunk_body(body: str, max_chars: int = DEFAULT_BODY_CHUNK_CHARS) -> list[str]:
    body = body.strip()
    if max_chars <= 0:
        raise ValueError("chunk size must be greater than zero")
    if len(body) <= max_chars:
        return [body]
    chunks: list[str] = []
    remaining = body
    while remaining:
        if len(remaining) <= max_chars:
            chunks.append(remaining)
            break
        cut = max(
            remaining.rfind("\n", 0, max_chars),
            remaining.rfind(". ", 0, max_chars),
            remaining.rfind("。", 0, max_chars),
        )
        if cut < int(max_chars * 0.5):
            cut = max_chars
        chunks.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    return chunks


def build_mailto_url(to: str, subject: str, body: str) -> str:
    query = urllib.parse.urlencode({"subject": subject, "body": body}, quote_via=urllib.parse.quote)
    return f"mailto:{urllib.parse.quote(to, safe='@,;<>')}?{query}"


def build_gmail_url(to: str, subject: str, body: str) -> str:
    params = {"view": "cm", "fs": "1", "to": to, "su": subject, "body": body}
    return "https://mail.google.com/mail/?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)


def build_urls(to: str, subject: str, body: str, max_chars: int = DEFAULT_BODY_CHUNK_CHARS, url_type: str = "mailto") -> list[dict[str, object]]:
    if url_type not in {"mailto", "gmail"}:
        raise ValueError("url_type must be 'mailto' or 'gmail'")
    parts = chunk_body(body, max_chars=max_chars)
    total = len(parts)
    results: list[dict[str, object]] = []
    for index, part in enumerate(parts, 1):
        label = f"[{index}/{total}] " if total > 1 else ""
        part_subject = label + subject
        part_body = label + part if total > 1 else part
        url = build_gmail_url(to, part_subject, part_body) if url_type == "gmail" else build_mailto_url(to, part_subject, part_body)
        results.append({"part": index, "total": total, "subject": part_subject, "url": url})
    return results
