from pathlib import Path

from email_agent.privacy import scan_paths


def test_privacy_scan_flags_env_and_secret_patterns(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("TOKEN=abc\n")
    source = tmp_path / "settings.py"
    source.write_text('api_key = "secret-value"\n')  # allow-secret

    findings = scan_paths([tmp_path])

    assert any(".env must not be committed" in item for item in findings)
    assert any("possible secret" in item for item in findings)


def test_privacy_scan_ignores_generated_frontend_dependencies(tmp_path: Path) -> None:
    generated = tmp_path / "frontend" / "node_modules" / "pkg"
    generated.mkdir(parents=True)
    (generated / "index.py").write_text('api_key = "example"\n')  # allow-secret

    assert scan_paths([tmp_path]) == []
