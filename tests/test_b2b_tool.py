# -*- coding: utf-8 -*-

import json
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "b2b_tool.py"


def make_docx(path: Path, lines: list[str]) -> Path:
    paragraphs = "".join(f"<w:p><w:r><w:t>{line}</w:t></w:r></w:p>" for line in lines)
    xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{paragraphs}</w:body></w:document>'''
    with ZipFile(path, "w", ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
        zf.writestr("word/document.xml", xml)
    return path


def run_cli(*args: str):
    return subprocess.run(
        [sys.executable, str(TOOL), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_parse_json_output(tmp_path):
    docx = make_docx(
        tmp_path / "customer.docx",
        [
            "公司名：PACIFIC RADIO",
            "国家：USA",
            "网站：https://example.com",
            "联系人：John Buyer",
            "邮箱：john@example.com",
            "主营产品：multimeters and test tools",
            "营收：USD 10M",
            "供应商：China OEM supplier",
            "痛点：needs certified high-margin supplementary line",
        ],
    )
    result = run_cli("parse", "--docx", str(docx), "--customer", "PACIFIC RADIO PYTEST", "--json")
    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert payload["command"] == "parse"
    assert payload["company"] == "PACIFIC RADIO"
    assert payload["email"] == "john@example.com"
    assert Path(ROOT / payload["memory"]["customer_json"]).exists()



def test_parse_selects_target_customer_section_not_loose_reference(tmp_path):
    docx = make_docx(
        tmp_path / "multi_customer.docx",
        [
            "公司名：Chauvin Arnoux",
            "国家：France",
            "备注：This paragraph mentions Pacific Radio only as a comparison, not as this section owner.",
            "痛点：wrong section",
            "公司名：PACIFIC RADIO",
            "国家：USA",
            "网站：https://pacific.example.com",
            "邮箱：buyer@pacific.example.com",
            "痛点：target section",
        ],
    )
    result = run_cli("parse", "--docx", str(docx), "--customer", "PACIFIC RADIO", "--json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert payload["matched_customer_section"] is True
    assert payload["company"] == "PACIFIC RADIO"
    assert payload["country"] == "USA"
    assert payload["email"] == "buyer@pacific.example.com"



def test_parse_heading_section_keeps_matching_company_label(tmp_path):
    docx = make_docx(
        tmp_path / "heading_customer.docx",
        [
            "## PACIFIC RADIO",
            "公司名：PACIFIC RADIO LTD",
            "国家：USA",
            "邮箱：team@pacific.example.com",
            "## NEXT CUSTOMER",
            "公司名：Other Customer",
            "国家：Canada",
        ],
    )
    result = run_cli("parse", "--docx", str(docx), "--customer", "PACIFIC RADIO", "--json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["matched_customer_section"] is True
    assert payload["company"] == "PACIFIC RADIO LTD"
    assert payload["country"] == "USA"
    assert payload["email"] == "team@pacific.example.com"

def test_legacy_header_argument_is_accepted_for_skill_compatibility(tmp_path):
    docx = make_docx(tmp_path / "customer.docx", ["公司名：PACIFIC RADIO", "国家：USA"])
    result = run_cli("parse", "--docx", str(docx), "--customer", "PACIFIC RADIO", "--header", "ignored", "--json")
    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads(result.stdout)["company"] == "PACIFIC RADIO"


def test_global_legacy_header_flag_is_accepted_before_subcommand(tmp_path):
    docx = make_docx(tmp_path / "customer.docx", ["公司名：PACIFIC RADIO", "国家：USA"])
    result = run_cli("--header", "parse", "--docx", str(docx), "--customer", "PACIFIC RADIO", "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout)["success"] is True

def test_gmail_link_json_output_and_chunking():
    body = "中文 & symbols " + ("x" * 2100)
    result = run_cli(
        "gmail-link",
        "--to",
        "3416393320@qq.com",
        "--subject",
        "开发邮件-PACIFIC RADIO",
        "--body",
        body,
        "--json",
    )
    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert payload["count"] == 2
    assert payload["urls"][0]["url"].startswith("mailto:")
    assert "%E4%B8%AD%E6%96%87" in payload["urls"][0]["url"]
    assert "%26" in payload["urls"][0]["url"]
    assert payload["urls"][0]["subject"].startswith("[1/2]")


def test_output_file_and_quiet(tmp_path):
    output = tmp_path / "result.json"
    result = run_cli(
        "gmail-link",
        "--to",
        "a@example.com",
        "--subject",
        "S",
        "--body",
        "Body",
        "--json",
        "--quiet",
        "--output",
        str(output),
    )
    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["success"] is True
    assert payload["urls"][0]["url"].startswith("mailto:")


def test_runtime_error_exit_code_and_json():
    result = run_cli("parse", "--docx", "missing.docx", "--customer", "NOPE", "--json")
    assert result.returncode == 1
    assert "docx file not found" in result.stderr
    payload = json.loads(result.stdout)
    assert payload == {"success": False, "error": "docx file not found: missing.docx"}


def test_parameter_error_exit_code():
    result = run_cli("gmail-link", "--json")
    assert result.returncode == 2
    assert result.stdout == ""
    assert "error:" in result.stderr


def test_all_subcommand_help():
    for command in ["parse", "backcheck", "mail-instruction", "gmail-link", "pipeline"]:
        result = run_cli(command, "--help")
        assert result.returncode == 0
        assert "usage:" in result.stdout
        assert result.stderr == ""
