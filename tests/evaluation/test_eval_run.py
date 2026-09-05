from pathlib import Path

from email_agent.evaluation.run import EvalConfig, run_evaluation


def test_baseline_eval_writes_report(tmp_path: Path) -> None:
    report_path = tmp_path / "report.json"

    report = run_evaluation(
        EvalConfig(
            dataset_path=Path("datasets/fixtures/dev.jsonl"),
            report_path=report_path,
        )
    )

    assert report_path.exists()
    assert report["baseline"] == "empty"
    assert report["total_records"] >= 1
    assert "scenario_results" in report
