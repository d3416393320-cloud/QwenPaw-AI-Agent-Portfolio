#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agent-friendly B2B development email automation CLI."""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path
from typing import Any

from core.backcheck import create_backcheck_prompt, create_mail_instruction, save_instruction
from core.gmail import DEFAULT_BODY_CHUNK_CHARS, build_urls
from core.parser import parse_docx_report, save_customer_memory
from core.utils import ensure_project_dirs, latest_backcheck_file, read_text_file, write_json_file, write_text_file

VERSION = "2.0.0"
DEFAULT_MAX_PROMPT_CHARS = 2000


class AgentArgumentParser(argparse.ArgumentParser):
    """Argparse subclass that returns exit code 2 for parameter errors."""

    def error(self, message: str) -> None:  # pragma: no cover - argparse plumbing
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {message}", file=sys.stderr)
        raise SystemExit(2)


def success_payload(command: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {"success": True, "command": command, **payload}


def failure_payload(error: Exception | str) -> dict[str, Any]:
    return {"success": False, "error": str(error)}


def as_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def emit_result(payload: dict[str, Any], args: argparse.Namespace, text_result: str | None = None) -> None:
    """Emit only the command result to stdout and/or --output."""
    if getattr(args, "json", False):
        output_text = as_json(payload)
    else:
        output_text = text_result if text_result is not None else human_text(payload)

    output_path = getattr(args, "output", None) or getattr(args, "out", None)
    if output_path:
        if getattr(args, "json", False):
            write_json_file(output_path, payload)
        else:
            write_text_file(output_path, output_text)

    # In quiet + output mode stdout stays silent; otherwise stdout is the clean result.
    if not (getattr(args, "quiet", False) and output_path):
        sys.stdout.write(output_text)
        if output_text and not output_text.endswith("\n"):
            sys.stdout.write("\n")


def human_text(payload: dict[str, Any]) -> str:
    if not payload.get("success", False):
        return f"ERROR: {payload.get('error', 'unknown error')}"
    command = payload.get("command")
    if command == "parse":
        keys = ["customer", "company", "country", "website", "contact", "email", "main_products", "revenue", "suppliers", "pain_points"]
        return "\n".join(f"{key}: {payload[key]}" for key in keys if payload.get(key))
    if command in {"backcheck", "mail-instruction"}:
        return str(payload.get("instruction", ""))
    if command == "gmail-link":
        return "\n".join(str(item["url"]) for item in payload.get("urls", []))
    if command == "pipeline":
        parts = []
        if payload.get("backcheck_instruction"):
            parts.append(str(payload["backcheck_instruction"]))
        if payload.get("mail_instruction"):
            parts.append(str(payload["mail_instruction"]))
        if payload.get("urls"):
            parts.extend(str(item["url"]) for item in payload["urls"])
        return "\n".join(parts)
    return as_json(payload)


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="输出标准JSON，推荐AI Agent统一使用。")
    parser.add_argument("--quiet", action="store_true", help="禁止非必要输出；配合--output时stdout保持为空。")
    parser.add_argument("--output", help="把结果写入指定文件。")
    # Backward compatibility for early skill drafts that passed --header.
    # It is intentionally ignored and hidden from --help; subcommands are the API.
    parser.add_argument("--header", nargs="?", default=None, help=argparse.SUPPRESS)


def cmd_parse(args: argparse.Namespace) -> dict[str, Any]:
    result = parse_docx_report(args.docx, args.customer or "")
    fields = result["fields"]
    memory = save_customer_memory(str(result["customer"]), fields, str(result["dump"]))
    payload = success_payload(
        "parse",
        {
            "customer": str(result["customer"]),
            **fields,
            "matched_customer_section": bool(result.get("matched_customer_section")),
            "memory": memory,
        },
    )
    if args.include_dump:
        payload["dump"] = str(result["dump"])
    return payload


def cmd_backcheck(args: argparse.Namespace) -> dict[str, Any]:
    result = create_backcheck_prompt(args.customer or "", args.input, args.max_chars)
    payload = success_payload("backcheck", result)
    if args.save_instruction:
        payload["instruction_file"] = save_instruction(args.save_instruction, str(result["instruction"]))
    return payload


def cmd_mail_instruction(args: argparse.Namespace) -> dict[str, Any]:
    result = create_mail_instruction(args.backcheck, args.max_chars)
    payload = success_payload("mail-instruction", result)
    if args.save_instruction:
        payload["instruction_file"] = save_instruction(args.save_instruction, str(result["instruction"]))
    return payload


def cmd_gmail_link(args: argparse.Namespace) -> dict[str, Any]:
    body = args.body if args.body is not None else read_text_file(args.body_file)
    urls = build_urls(args.to, args.subject, body, max_chars=args.chunk_chars, url_type=args.type)
    return success_payload("gmail-link", {"to": args.to, "subject": args.subject, "type": args.type, "count": len(urls), "urls": urls})


def cmd_pipeline(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {"customer": args.customer, "phase": "backcheck_ready"}

    if not args.resume:
        if not args.docx:
            raise ValueError("--docx is required unless --resume is used")
        parsed = parse_docx_report(args.docx, args.customer)
        memory = save_customer_memory(str(parsed["customer"]), parsed["fields"], str(parsed["dump"]))
        customer_data = {"customer": str(parsed["customer"]), **parsed["fields"]}
        instruction_result = create_backcheck_prompt(input_path=memory["customer_json"], max_chars=args.max_chars)
        payload.update({
            "customer": str(parsed["customer"]),
            "memory": memory,
            "backcheck_instruction": instruction_result["instruction"],
            "backcheck_chars": instruction_result["chars"],
            "fields": customer_data,
            "matched_customer_section": bool(parsed.get("matched_customer_section")),
        })

    backcheck_path = args.backcheck
    if not backcheck_path and args.resume:
        found = latest_backcheck_file(args.customer)
        backcheck_path = str(found) if found else None

    if backcheck_path:
        mail_result = create_mail_instruction(backcheck_path, args.max_chars)
        payload.update({
            "phase": "mail_ready",
            "backcheck": backcheck_path,
            "mail_instruction": mail_result["instruction"],
            "mail_chars": mail_result["chars"],
        })
        if args.to:
            body = args.body if args.body is not None else ""
            urls = build_urls(args.to, args.subject or f"开发邮件-{args.customer}", body, max_chars=args.chunk_chars, url_type=args.type)
            payload.update({"urls": urls, "url_count": len(urls)})
    else:
        payload["next_required"] = "backcheck file path via --backcheck"

    return success_payload("pipeline", payload)


def build_parser() -> argparse.ArgumentParser:
    parser = AgentArgumentParser(
        prog="b2b_tool.py",
        description="Agent-friendly B2B开发邮件自动化CLI（Python 3.10+，标准库实现）。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
        推荐给AI Agent调用：
          python b2b_tool.py parse --docx "reports/a.docx" --customer "PACIFIC RADIO" --json
          python b2b_tool.py backcheck --customer "PACIFIC RADIO" --json
          python b2b_tool.py mail-instruction --backcheck "memory/背调_PACIFIC_RADIO_2026-05-12.txt" --json
          python b2b_tool.py gmail-link --to "3416393320@qq.com" --subject "开发邮件-PACIFIC RADIO" --body-file "邮件正文.txt" --json

        stdout: only command result. stderr: errors only. exit codes: 0 success, 1 runtime failure, 2 parameter error.
        """),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("--header", action="store_true", help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("parse", help="解析.docx客户报告。")
    add_common_options(p)
    p.add_argument("--docx", required=True, help="客户报告.docx路径。")
    p.add_argument("--customer", default="", help="客户名。")
    p.add_argument("--include-dump", action="store_true", help="JSON结果中包含完整文本dump。")
    p.set_defaults(func=cmd_parse)

    p = sub.add_parser("backcheck", help="生成Gem1背调标准指令。")
    add_common_options(p)
    p.add_argument("--customer", default="", help="客户名；未提供--input时用于读取memory/customer_xxx.json。")
    p.add_argument("--input", help="parse生成的客户JSON文件。")
    p.add_argument("--max-chars", type=int, default=DEFAULT_MAX_PROMPT_CHARS, help="指令最大字符数，默认2000。")
    p.add_argument("--save-instruction", help="仅保存instruction纯文本到指定文件。")
    p.set_defaults(func=cmd_backcheck)

    p = sub.add_parser("mail-instruction", help="读取Gem1背调结果，生成Gem2开发邮件指令。")
    add_common_options(p)
    p.add_argument("--backcheck", required=True, help="Gem1背调结果文本路径。")
    p.add_argument("--max-chars", type=int, default=DEFAULT_MAX_PROMPT_CHARS, help="指令最大字符数，默认2000。")
    p.add_argument("--save-instruction", help="仅保存instruction纯文本到指定文件。")
    p.set_defaults(func=cmd_mail_instruction)

    p = sub.add_parser("gmail-link", help="生成URL编码正确的mailto或Gmail撰写链接。")
    add_common_options(p)
    p.add_argument("--to", required=True, help="收件人邮箱。")
    p.add_argument("--subject", required=True, help="邮件主题。")
    body = p.add_mutually_exclusive_group(required=True)
    body.add_argument("--body", help="邮件正文文本。")
    body.add_argument("--body-file", help="邮件正文文件路径。")
    p.add_argument("--chunk-chars", type=int, default=DEFAULT_BODY_CHUNK_CHARS, help="正文分片字符数，默认2000。")
    p.add_argument("--type", choices=("mailto", "gmail"), default="mailto", help="输出URL类型。")
    p.set_defaults(func=cmd_gmail_link)

    p = sub.add_parser("pipeline", help="无交互两阶段流程：DOCX→Gem1指令→Gem2指令→可选URL。")
    add_common_options(p)
    p.add_argument("--docx", help="客户报告.docx路径；--resume时可省略。")
    p.add_argument("--customer", required=True, help="客户名。")
    p.add_argument("--resume", action="store_true", help="跳过DOCX解析，从memory/背调文件或--backcheck继续。")
    p.add_argument("--backcheck", help="Gem1背调结果文本路径。")
    p.add_argument("--max-chars", type=int, default=DEFAULT_MAX_PROMPT_CHARS, help="Gem指令最大字符数，默认2000。")
    p.add_argument("--to", help="可选：生成审核邮箱URL。")
    p.add_argument("--subject", help="可选：审核邮件主题。")
    p.add_argument("--body", help="可选：审核邮件正文。")
    p.add_argument("--chunk-chars", type=int, default=DEFAULT_BODY_CHUNK_CHARS, help="URL正文分片字符数，默认2000。")
    p.add_argument("--type", choices=("mailto", "gmail"), default="mailto", help="输出URL类型。")
    p.set_defaults(func=cmd_pipeline)

    return parser


def main(argv: list[str] | None = None) -> int:
    ensure_project_dirs()
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2

    try:
        payload = args.func(args)
        emit_result(payload, args)
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        error_payload = failure_payload(exc)
        # Runtime failures still emit machine-readable result when --json was requested.
        if "args" in locals() and getattr(args, "json", False):
            emit_result(error_payload, args)
        return 1


if __name__ == "__main__":
    sys.exit(main())
