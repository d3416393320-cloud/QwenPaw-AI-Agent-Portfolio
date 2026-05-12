# -*- coding: utf-8 -*-
"""Embedded prompts for Gemini Gems."""

from __future__ import annotations

import json
import textwrap

from .utils import normalize_lines, truncate_text

DEFAULT_MAX_PROMPT_CHARS = 2000


def _fit_prompt(header: str, body: str, max_chars: int = DEFAULT_MAX_PROMPT_CHARS) -> str:
    available = max(100, max_chars - len(header) - 1)
    return (header + truncate_text(body, available)).strip()


def build_backcheck_instruction(customer_data: dict[str, object], max_chars: int = DEFAULT_MAX_PROMPT_CHARS) -> str:
    customer = str(customer_data.get("customer") or customer_data.get("company") or "客户")
    compact = json.dumps(customer_data, ensure_ascii=False, separators=(",", ":"))
    header = textwrap.dedent(f"""
    请作为外贸B2B客户开发研究员，对以下客户做深度商业背调，并输出可直接用于开发邮件的结论。

    目标客户：{customer}
    研究要求：
    1. 核实公司主营业务、采购偏好、目标市场与潜在联系人。
    2. 判断其现有产品线/供应商/进口背景，找出可切入的补充产品机会。
    3. 重点挖掘痛点：利润、认证、交期、包装、品牌/OEM、售后、合规风险。
    4. 推荐“高利润补充线”，说明不是替代现有品牌，而是帮助其扩充利润品类。
    5. 输出：客户画像、证据线索、痛点、推荐产品方向、开发邮件切入角度。

    客户资料JSON：
    """).lstrip()
    return _fit_prompt(header, compact, max_chars=max_chars)


def essence_from_backcheck(text: str, max_chars: int = 1600) -> str:
    lines = normalize_lines(text)
    keywords = [
        "痛点", "机会", "推荐", "产品", "供应商", "进口", "采购", "利润", "认证", "OEM",
        "pain", "opportunity", "recommend", "product", "supplier", "import", "buyer", "margin", "cert",
    ]
    picked: list[str] = []
    for line in lines:
        lower = line.lower()
        if any(keyword.lower() in lower for keyword in keywords) and line not in picked:
            picked.append(line)
        if len(picked) >= 18:
            break
    essence = "\n".join(picked) if picked else text
    return truncate_text(essence, max_chars)


def build_mail_instruction(backcheck_text: str, max_chars: int = DEFAULT_MAX_PROMPT_CHARS) -> str:
    header = textwrap.dedent("""
    基于以下客户背调信息，生成外贸B2B英文开发邮件，并附中文对照用于审核。

    写作要求：
    1. 输出收件人建议、英文主题行、英文邮件正文、中文对照说明。
    2. 邮件定位为“高利润补充线”，强调补充其现有产品组合，不攻击/替代现有品牌。
    3. 语气专业、简洁、可信，不夸大；包含1个明确CTA（回复确认是否可寄目录/报价）。
    4. 英文正文控制在180词以内；避免垃圾邮件词和过度营销。
    5. 如信息不足，请基于背调线索做保守假设，并在中文对照中标注。

    背调精华：
    """).lstrip()
    return _fit_prompt(header, essence_from_backcheck(backcheck_text), max_chars=max_chars)
