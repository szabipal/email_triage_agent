from pathlib import Path

from email_agent.privacy import scan_paths


def main() -> int:
    findings = scan_paths([Path(".")])
    if findings:
        print("\n".join(findings))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
