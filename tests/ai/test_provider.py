from pydantic import ValidationError

from email_agent.ai import LLMRequest, LLMResponse


def test_llm_contract_carries_prompt_schema_timeout_and_model_metadata() -> None:
    request = LLMRequest(
        prompt="Analyze this email.",
        schema_name="EmailAnalysisSignals",
        prompt_version="analysis-v1",
        model="fake-llm",
        timeout_seconds=5,
        max_retries=1,
    )
    response = LLMResponse(
        output={"summary": "Ada asks for review."},
        model_name=request.model,
        prompt_version=request.prompt_version,
        schema_version="signals-v1",
    )

    assert request.timeout_seconds == 5
    assert response.model_name == "fake-llm"


def test_llm_contract_rejects_missing_prompt_metadata() -> None:
    try:
        LLMRequest(
            prompt="Analyze.",
            schema_name="EmailAnalysisSignals",
            prompt_version="",
            model="fake-llm",
        )
    except ValidationError as error:
        assert "prompt_version" in str(error)
    else:
        raise AssertionError("empty prompt_version should fail")
