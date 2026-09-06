from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, ValidationError

from email_agent.ai.prompts import (
    ANALYSIS_SCHEMA_VERSION,
    ANALYSIS_VERSION,
    render_analysis_prompt,
)
from email_agent.ai.provider import LLMError, LLMProvider, LLMRequest
from email_agent.domain import EmailAnalysisSignals, ProcessedEmail


class SignalRepository(Protocol):
    def save_signals(self, signals: EmailAnalysisSignals) -> None: ...


class AnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    signals: EmailAnalysisSignals | None = None
    errors: list[str] = []


class AnalysisService:
    def __init__(
        self,
        provider: LLMProvider,
        *,
        model: str = "fake-llm",
        output_language: str = "en",
        timeout_seconds: float = 30,
        max_retries: int = 0,
    ) -> None:
        self.provider = provider
        self.model = model
        self.output_language = output_language
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    def analyze(
        self,
        processed_email: ProcessedEmail,
        repository: SignalRepository | None = None,
    ) -> AnalysisResult:
        request = LLMRequest(
            prompt=render_analysis_prompt(
                processed_email,
                output_language=self.output_language,
            ),
            schema_name=ANALYSIS_SCHEMA_VERSION,
            prompt_version=ANALYSIS_VERSION,
            model=self.model,
            timeout_seconds=self.timeout_seconds,
            max_retries=self.max_retries,
        )
        errors: list[str] = []
        for _ in range(request.max_retries + 1):
            try:
                response = self.provider.complete_structured(request)
                signals = EmailAnalysisSignals.model_validate(
                    response.output
                    | {
                        "model_name": response.model_name,
                        "prompt_version": response.prompt_version,
                        "schema_version": response.schema_version,
                    }
                )
                break
            except (LLMError, TimeoutError, ValidationError) as error:
                errors.append(str(error))
        else:
            return AnalysisResult(errors=errors)

        if repository is not None:
            repository.save_signals(signals)
        return AnalysisResult(signals=signals)
