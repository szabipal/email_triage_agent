from __future__ import annotations

import re
from pathlib import Path

SECRET_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"api[_-]?key\s*=\s*['\"][^'\"]+",
        r"secret\s*=\s*['\"][^'\"]+",
        r"password\s*=\s*['\"][^'\"]+",
        r"-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----",
    )
]
SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    ".pytest_cache",
    ".ruff_cache",
    ".pyright",
}


def scan_paths(paths: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        if path.is_file():
            _scan_file(path, findings)
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and not (set(child.parts) & SKIP_DIRS):
                    _scan_file(child, findings)
    return findings


def _scan_file(path: Path, findings: list[str]) -> None:
    if path.name == ".env":
        findings.append(f"{path}: .env must not be committed")
        return
    try:
        text = path.read_text()
    except UnicodeDecodeError:
        return
    for line_number, line in enumerate(text.splitlines(), start=1):
        if "allow-secret" in line:
            continue
        if any(pattern.search(line) for pattern in SECRET_PATTERNS):
            findings.append(f"{path}:{line_number}: possible secret")
