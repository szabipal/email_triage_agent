from pathlib import Path

from email_agent.evaluation.llm_smoke import run_llm_analysis_smoke


def test_llm_analysis_smoke_writes_predictions_with_model_metadata(
    tmp_path: Path,
) -> None:
    predictions_path = tmp_path / "predictions.json"

    predictions = run_llm_analysis_smoke(
        Path("datasets/fixtures/dev.jsonl"),
        predictions_path,
        limit=2,
    )

    assert predictions_path.exists()
    assert len(predictions) == 2
    signals = predictions[0]["signals"]
    assert isinstance(signals, dict)
    assert signals["model_name"] == "fake-llm"
    assert signals["prompt_version"] == "analysis-v1"
    assert signals["schema_version"] == "signals-v1"
