# -*- coding: utf-8 -*-
"""DOCX text extraction and customer field parsing."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from .utils import memory_path, normalize_lines, write_json_file, write_text_file

FIELD_ORDER = [
    "customer",
    "company",
    "country",
    "website",
    "contact",
    "email",
    "main_products",
    "revenue",
    "suppliers",
    "pain_points",
]

FIELD_PATTERNS = {
    "company": ["公司名", "公司名称", "客户名称", "企业名称", "company", "name"],
    "country": ["国家", "地区", "country", "location", "market"],
    "website": ["网站", "官网", "网址", "website", "web", "url"],
    "contact": ["联系人", "采购", "负责人", "contact", "buyer", "person"],
    "email": ["邮箱", "邮件", "email", "e-mail", "mail"],
    "main_products": ["主营产品", "主营业务", "产品", "业务", "main products", "products", "business"],
    "revenue": ["营收", "收入", "销售额", "年销售", "revenue", "sales", "turnover"],
    "suppliers": ["供应商", "进口商", "采购来源", "supplier", "suppliers", "vendor"],
    "pain_points": ["痛点", "需求", "机会", "风险", "关注", "pain", "need", "challenge", "opportunity"],
}

KEYWORD_GROUPS = {
    "pain_points": ["痛点", "需求", "机会", "风险", "利润", "认证", "缺", "替代", "pain", "need", "challenge", "opportunity", "risk", "margin", "cert"],
    "suppliers": ["供应商", "制造商", "进口", "海关", "supplier", "vendor", "manufacturer", "import"],
    "main_products": ["主营", "产品", "型号", "品类", "product", "model", "category", "line"],
}


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def xml_text_from_docx_part(xml_bytes: bytes) -> str:
    root = ET.fromstring(xml_bytes)
    out: list[str] = []

    def walk(node: ET.Element) -> None:
        tag = _local_name(node.tag)
        if tag == "t" and node.text:
            out.append(node.text)
        elif tag == "tab":
            out.append("\t")
        elif tag in ("br", "cr"):
            out.append("\n")
        for child in list(node):
            walk(child)
        if tag in ("p", "tr"):
            out.append("\n")
        elif tag == "tc":
            out.append("\t")

    walk(root)
    text = "".join(out)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_docx_text(docx_path: str | Path) -> str:
    path = Path(docx_path)
    if not path.exists():
        raise FileNotFoundError(f"docx file not found: {path}")
    if path.suffix.lower() != ".docx":
        raise ValueError(f"not a .docx file: {path}")

    parts: list[str] = []
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        wanted = ["word/document.xml"]
        wanted.extend(sorted(n for n in names if re.match(r"word/(header|footer|footnotes|endnotes)\d*\.xml$", n)))
        for name in wanted:
            if name in names:
                piece = xml_text_from_docx_part(zf.read(name))
                if piece:
                    parts.append(piece)
    return "\n\n".join(parts).strip()



def _norm_key(value: str) -> str:
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", value.lower())


def _is_customer_label_line(line: str) -> bool:
    labels = FIELD_PATTERNS["company"] + ["客户", "customer"]
    return any(re.search(rf"(?:^|[\s\|｜]){re.escape(label)}\s*[:：\-]", line, re.I) for label in labels)


def _line_label_value(line: str) -> str:
    for label in FIELD_PATTERNS["company"] + ["客户", "customer"]:
        value = _value_from_labeled_line(line, [label])
        if value:
            return value
    return ""


def _is_target_heading(line: str, target_norm: str) -> bool:
    stripped = line.strip(" #*-—–_\t")
    line_norm = _norm_key(stripped)
    if not line_norm or target_norm not in line_norm:
        return False
    # Weak matches are accepted only for short heading-like lines, not long notes
    # such as "Chauvin Arnoux ... mentioned Pacific Radio ...".
    return len(line_norm) <= max(len(target_norm) + 12, int(len(target_norm) * 1.6))


def select_customer_section(text: str, customer: str) -> tuple[str, bool]:
    """Return the section most likely belonging to ``customer``.

    The matcher prefers explicit section labels/headings (for example
    "公司名：PACIFIC RADIO") and avoids loose substring hits inside another
    customer's notes.
    """
    target_norm = _norm_key(customer)
    if not target_norm:
        return text, False

    raw_lines = text.splitlines()
    lines = [line for line in raw_lines]
    start_index: int | None = None

    for index, line in enumerate(lines):
        value = _line_label_value(line)
        if value and _norm_key(value) == target_norm:
            start_index = index
            break

    if start_index is None:
        for index, line in enumerate(lines):
            if _is_target_heading(line, target_norm):
                start_index = index
                break

    if start_index is None:
        return text, False

    end_index = len(lines)
    for index in range(start_index + 1, len(lines)):
        line = lines[index]
        if _is_customer_label_line(line):
            value_norm = _norm_key(_line_label_value(line))
            if value_norm and (target_norm in value_norm or value_norm in target_norm):
                continue
            end_index = index
            break
        stripped = line.strip()
        if stripped.startswith(("# ", "## ", "### ")) and index > start_index + 1:
            end_index = index
            break

    section = "\n".join(lines[start_index:end_index]).strip()
    return (section or text), True

def _value_from_labeled_line(line: str, labels: list[str]) -> str:
    for label in labels:
        pattern = re.compile(rf"(?:^|[\s\|｜]){re.escape(label)}\s*[:：\-]\s*(.+)$", re.I)
        match = pattern.search(line)
        if match:
            return match.group(1).strip(" \t;；,，")
    return ""


def _first_regex(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.I)
    return match.group(0).strip() if match else ""


def _collect_keyword_lines(lines: list[str], keywords: list[str], limit: int = 6) -> list[str]:
    found: list[str] = []
    for line in lines:
        lower = line.lower()
        if any(k.lower() in lower for k in keywords) and line not in found:
            found.append(line)
        if len(found) >= limit:
            break
    return found


def extract_fields(text: str, customer: str = "") -> dict[str, str]:
    lines = normalize_lines(text)
    fields = {key: "" for key in FIELD_ORDER}
    fields["customer"] = customer.strip()

    for key, labels in FIELD_PATTERNS.items():
        for line in lines:
            value = _value_from_labeled_line(line, labels)
            if value:
                fields[key] = value[:500]
                break

    if not fields["email"]:
        fields["email"] = _first_regex(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", text)
    if not fields["website"]:
        fields["website"] = _first_regex(r"https?://[^\s)）>]+|www\.[^\s)）>]+", text)
    if not fields["company"]:
        fields["company"] = customer.strip() or (lines[0][:120] if lines else "")

    for key in ("pain_points", "suppliers", "main_products"):
        if not fields[key]:
            fields[key] = "；".join(_collect_keyword_lines(lines, KEYWORD_GROUPS[key]))[:900]

    return {key: fields[key] for key in FIELD_ORDER if fields.get(key)}


def parse_docx_report(docx_path: str | Path, customer: str = "") -> dict[str, object]:
    text = extract_docx_text(docx_path)
    parse_text, matched_section = select_customer_section(text, customer) if customer else (text, False)
    fields = extract_fields(parse_text, customer)
    return {
        "customer": fields.get("customer") or customer or fields.get("company", ""),
        "fields": fields,
        "dump": text,
        "parsed_text": parse_text,
        "matched_customer_section": matched_section,
    }


def save_customer_memory(customer: str, fields: dict[str, str], dump: str) -> dict[str, str]:
    name = customer or fields.get("customer") or fields.get("company") or "customer"
    stable_json = memory_path(name, "customer", "json", dated=False)
    dated_json = memory_path(name, "customer", "json", dated=True)
    dump_txt = memory_path(name, "dump", "txt", dated=True)
    payload = {"success": True, "customer": name, **fields}
    write_json_file(stable_json, payload)
    write_json_file(dated_json, payload)
    write_text_file(dump_txt, dump)
    return {"customer_json": str(stable_json), "customer_json_dated": str(dated_json), "dump_txt": str(dump_txt)}
