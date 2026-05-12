# -*- coding: utf-8 -*-
"""Example: call b2b_tool.py from an AI Agent process."""

import json
import subprocess

result = subprocess.run(
    [
        "python",
        "b2b_tool.py",
        "parse",
        "--docx",
        "test.docx",
        "--customer",
        "PACIFIC RADIO",
        "--json",
    ],
    capture_output=True,
    text=True,
    encoding="utf-8",
)

if result.returncode != 0:
    raise RuntimeError(result.stderr.strip() or result.stdout.strip())

data = json.loads(result.stdout)
print(data)
