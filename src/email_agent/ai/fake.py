from __future__ import annotations

from email_agent.ai.provider import LLMError, LLMRequest, LLMResponse


class FakeLLMProvider:
    def __init__(
        self,
        outputs: dict[str, dict[str, object]],
        *,
        errors: set[str] | None = None,
    ) -> None:
        self.outputs = outputs
        self.errors = errors or set()
        self.requests: list[LLMRequest] = []

    def complete_structured(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        if request.prompt in self.errors:
            raise LLMError(f"fake LLM error for prompt: {request.prompt}")

        return LLMResponse(
            output=self.outputs[request.prompt],
            model_name=request.model,
            prompt_version=request.prompt_version,
            schema_version=request.schema_name,
        )
