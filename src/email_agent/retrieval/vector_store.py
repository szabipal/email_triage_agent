from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import chromadb
from pydantic import BaseModel, ConfigDict, Field


class VectorDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    embedding: list[float] = Field(min_length=1)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class VectorMatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    text: str
    distance: float
    metadata: dict[str, str | int | float | bool]


class ChromaIndex:
    def __init__(self, path: Path, *, collection_name: str = "emails") -> None:
        self.collection = chromadb.PersistentClient(
            path=str(path)
        ).get_or_create_collection(collection_name)

    def add(self, document: VectorDocument) -> None:
        self.collection.upsert(
            ids=[document.id],
            documents=[document.text],
            embeddings=[document.embedding],
            metadatas=[cast(dict[str, Any], document.metadata)],
        )

    def query(self, embedding: list[float], *, limit: int = 3) -> list[VectorMatch]:
        result: Any = self.collection.query(
            query_embeddings=[embedding],
            n_results=limit,
            include=cast(Any, ["documents", "metadatas", "distances"]),
        )
        ids = result["ids"][0]
        documents = result["documents"][0]
        metadatas = result["metadatas"][0]
        distances = result["distances"][0]
        return [
            VectorMatch(
                id=id_,
                text=document,
                distance=distance,
                metadata=cast(dict[str, str | int | float | bool], metadata or {}),
            )
            for id_, document, distance, metadata in zip(
                ids,
                documents,
                distances,
                metadatas,
                strict=True,
            )
        ]
