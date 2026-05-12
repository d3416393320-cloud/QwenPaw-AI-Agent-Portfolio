# Agent Integration Guide for `b2b_tool.py`

`b2b_tool.py` is designed as a deterministic command-line tool for QwenPaw Agent, Browser Agent, Gemini Automation, and future MCP wrappers.

## 1. How Agents Should Call It

Agents should call subcommands with `--json` and parse `stdout` as JSON:

```bash
python b2b_tool.py parse --docx "reports/customer.docx" --customer "PACIFIC RADIO" --json
```

Recommended subcommands:

- `parse`: parse a DOCX customer report and save `memory/customer_<customer>.json`.
- `backcheck`: generate the Gem1 backcheck prompt.
- `mail-instruction`: generate the Gem2 email prompt from a saved backcheck file.
- `gmail-link`: generate URL-encoded `mailto:` or Gmail compose URLs.
- `pipeline`: run the non-interactive staged workflow.

## 2. Python `subprocess` Example

```python
import json
import subprocess

result = subprocess.run(
    [
        "python",
        "b2b_tool.py",
        "parse",
        "--docx",
        "reports/customer.docx",
        "--customer",
        "PACIFIC RADIO",
        "--json",
    ],
    capture_output=True,
    text=True,
    encoding="utf-8",
)

payload = json.loads(result.stdout)
if result.returncode != 0 or not payload["success"]:
    raise RuntimeError(result.stderr or payload.get("error"))
```

## 3. stdout / stderr Contract

- `stdout` contains only the command result.
- With `--json`, `stdout` is a single compact JSON object.
- `stderr` is reserved for errors.
- No debug logs, emojis, or explanatory text are printed to `stdout`.

For runtime failures with `--json`, the tool emits a JSON failure object to `stdout` and the error message to `stderr`.

## 4. Exit Code Contract

| Exit code | Meaning |
| --- | --- |
| `0` | Success |
| `1` | Runtime failure, such as missing DOCX/backcheck file |
| `2` | Parameter/usage error from argparse |

## 5. JSON Output Format

All JSON results include:

```json
{
  "success": true,
  "command": "parse"
}
```

Runtime failure shape:

```json
{
  "success": false,
  "error": "docx file not found: reports/missing.docx"
}
```

`parse` adds customer fields and memory paths:

```json
{
  "success": true,
  "command": "parse",
  "customer": "PACIFIC RADIO",
  "company": "PACIFIC RADIO",
  "country": "USA",
  "memory": {
    "customer_json": "memory/customer_PACIFIC_RADIO.json"
  }
}
```

`gmail-link` returns URL parts:

```json
{
  "success": true,
  "command": "gmail-link",
  "count": 2,
  "urls": [
    {"part": 1, "total": 2, "url": "mailto:..."}
  ]
}
```

## 6. Recommended Agent Workflow

1. Agent receives a DOCX path and customer name.
2. Run `parse --json` and store parsed JSON path from `memory.customer_json`.
3. Run `backcheck --customer <name> --json`.
4. Browser Agent pastes `instruction` into Gem1.
5. Save Gem1 output as `memory/backcheck_<customer>.txt` or `memory/背调_<customer>_<date>.txt`.
6. Run `mail-instruction --backcheck <file> --json`.
7. Browser Agent pastes `instruction` into Gem2.
8. Run `gmail-link --json` with the final reviewed body when a compose URL is needed.

## 7. QwenPaw / Browser Agent Suggestions

- Always pass `--json`.
- Use `capture_output=True` and parse only `stdout`.
- Treat non-zero exit codes as failed tool calls.
- Do not rely on human-readable default output for automation.
- Prefer `--output output/result.json` for long-running batch jobs that need durable artifacts.
- Use `--quiet --output <file>` when another orchestrator only needs a file artifact and not stdout.

## 8. Upgrade Path to MCP Tool

This CLI can become an MCP tool by wrapping each subcommand as a tool handler:

- `parse_docx_report(docx, customer)` → invokes `core.parser.parse_docx_report`.
- `create_backcheck_prompt(customer|input)` → invokes `core.backcheck.create_backcheck_prompt`.
- `create_mail_instruction(backcheck)` → invokes `core.backcheck.create_mail_instruction`.
- `create_gmail_links(to, subject, body)` → invokes `core.gmail.build_urls`.

The `core/` modules are intentionally side-effect-light and can be imported directly by an MCP server without shelling out.
