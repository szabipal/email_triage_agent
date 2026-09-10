import subprocess
from pathlib import Path

from email_agent.privacy import scan_paths


def main() -> int:
    findings = scan_paths(_tracked_paths())
    if findings:
        print("\n".join(findings))
        return 1
    return 0


def _tracked_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(line) for line in result.stdout.splitlines()]


if __name__ == "__main__":
    raise SystemExit(main())
