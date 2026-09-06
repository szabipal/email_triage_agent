import pytest
from pydantic import ValidationError

from email_agent.retrieval import Embedding, EmbeddingRequest, FakeEmbeddingProvider


def test_embedding_contract_carries_model_version_and_dimension() -> None:
    embedding = Embedding(
        vector=[0.1, 0.2],
        model_name="fake-embedding",
        model_version="v1",
        dimension=2,
    )

    assert embedding.model_name == "fake-embedding"
    assert EmbeddingRequest(text="hello").text == "hello"


def test_embedding_rejects_dimension_mismatch() -> None:
    with pytest.raises(ValidationError, match="vector length"):
        Embedding(
            vector=[0.1],
            model_name="fake-embedding",
            model_version="v1",
            dimension=2,
        )


def test_fake_embedding_provider_is_deterministic() -> None:
    provider = FakeEmbeddingProvider(dimension=4)

    first = provider.embed(EmbeddingRequest(text="same text"))
    second = provider.embed(EmbeddingRequest(text="same text"))

    assert first == second
    assert len(first.vector) == 4
