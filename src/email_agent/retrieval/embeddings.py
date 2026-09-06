from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EmbeddingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)


class Embedding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vector: list[float] = Field(min_length=1)
    model_name: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    dimension: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_dimension(self) -> Embedding:
        if len(self.vector) != self.dimension:
            raise ValueError("embedding vector length must match dimension")
        return self


class EmbeddingProvider(Protocol):
    def embed(self, request: EmbeddingRequest) -> Embedding: ...
