# -*- coding: utf-8 -*-
"""Backcheck and mail-instruction orchestration helpers."""

from __future__ import annotations

from pathlib import Path

from .prompts import build_backcheck_instruction, build_mail_instruction
from .utils import latest_customer_json, load_json_file, read_text_file, write_text_file


def load_customer_data(customer: str = "", input_path: str | Path | None = None) -> dict[str, object]:
    if input_path:
        return load_json_file(input_path)
    if not customer:
        raise ValueError("customer is required when --input is not provided")
    return load_json_file(latest_customer_json(customer))


def create_backcheck_prompt(customer: str = "", input_path: str | Path | None = None, max_chars: int = 2000) -> dict[str, object]:
    data = load_customer_data(customer, input_path)
    prompt = build_backcheck_instruction(data, max_chars=max_chars)
    return {"customer": str(data.get("customer") or customer or data.get("company") or ""), "instruction": prompt, "chars": len(prompt)}


def create_mail_instruction(backcheck_path: str | Path, max_chars: int = 2000) -> dict[str, object]:
    text = read_text_file(backcheck_path)
    prompt = build_mail_instruction(text, max_chars=max_chars)
    return {"backcheck": str(backcheck_path), "instruction": prompt, "chars": len(prompt)}


def save_instruction(path: str | Path, instruction: str) -> str:
    return str(write_text_file(path, instruction))
