from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field


class LLMRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(min_length=1)
    schema_name: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)
    model: str = Field(min_length=1)
    timeout_seconds: float = Field(default=30, gt=0)
    max_retries: int = Field(default=0, ge=0)
    json_schema: dict[str, object] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    output: dict[str, object]
    model_name: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)
    schema_version: str = Field(min_length=1)


class LLMError(RuntimeError):
    pass


class LLMProvider(Protocol):
    def complete_structured(self, request: LLMRequest) -> LLMResponse: ...
