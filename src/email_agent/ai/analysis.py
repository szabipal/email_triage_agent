from __future__ import annotations

import time
from typing import Protocol

from pydantic import BaseModel, ConfigDict, ValidationError

from email_agent.ai.prompts import (
    ANALYSIS_SCHEMA_VERSION,
    ANALYSIS_VERSION,
    render_analysis_prompt,
)
from email_agent.ai.provider import LLMError, LLMProvider, LLMRequest
from email_agent.domain import EmailAnalysisSignals, ProcessedEmail
from email_agent.logging import get_logger, log_event

logger = get_logger(__name__)


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
        max_body_chars: int | None = None,
    ) -> None:
        self.provider = provider
        self.model = model
        self.output_language = output_language
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.max_body_chars = max_body_chars

    def analyze(
        self,
        processed_email: ProcessedEmail,
        repository: SignalRepository | None = None,
        context: list[str] | None = None,
    ) -> AnalysisResult:
        request = LLMRequest(
            prompt=render_analysis_prompt(
                processed_email,
                output_language=self.output_language,
                context=context,
                max_body_chars=self.max_body_chars,
            ),
            schema_name=ANALYSIS_SCHEMA_VERSION,
            prompt_version=ANALYSIS_VERSION,
            model=self.model,
            timeout_seconds=self.timeout_seconds,
            max_retries=self.max_retries,
            json_schema=EmailAnalysisSignals.model_json_schema(),
        )
        errors: list[str] = []
        for attempt in range(request.max_retries + 1):
            started = time.perf_counter()
            try:
                response = self.provider.complete_structured(request)
                signals = EmailAnalysisSignals.model_validate(
                    response.output
                    | {
                        "model_name": response.model_name,
                        "prompt_version": response.prompt_version,
                        "schema_version": response.schema_version,
                        "input_tokens": response.input_tokens,
                        "output_tokens": response.output_tokens,
                        "total_tokens": response.total_tokens,
                        "estimated_cost_usd": response.estimated_cost_usd,
                    }
                )
                log_event(
                    logger,
                    "llm analysis completed",
                    email_id=processed_email.email_id,
                    stage="llm",
                    latency_ms=_elapsed_ms(started),
                    fields={
                        "model": request.model,
                        "retry_count": attempt,
                        "total_tokens": response.total_tokens,
                    },
                )
                break
            except (LLMError, TimeoutError, ValidationError) as error:
                error_name = type(error).__name__
                errors.append(error_name)
                log_event(
                    logger,
                    "llm analysis failed",
                    email_id=processed_email.email_id,
                    stage="llm",
                    latency_ms=_elapsed_ms(started),
                    fields={
                        "model": request.model,
                        "retry_count": attempt,
                        "error_type": error_name,
                    },
                )
        else:
            return AnalysisResult(errors=errors)

        if repository is not None:
            repository.save_signals(signals)
        return AnalysisResult(signals=signals)


def _elapsed_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 3)
