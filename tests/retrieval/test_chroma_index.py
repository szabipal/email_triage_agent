from email_agent.retrieval import (
    ChromaIndex,
    EmbeddingRequest,
    FakeEmbeddingProvider,
    VectorDocument,
)


def test_chroma_index_retrieves_indexed_fixture_by_id(tmp_path) -> None:
    provider = FakeEmbeddingProvider(dimension=8)
    text = "legal approved the vendor exception for invoice INV-4421"
    embedding = provider.embed(EmbeddingRequest(text=text))
    index = ChromaIndex(tmp_path)

    index.add(
        VectorDocument(
            id="email-dev-007",
            text=text,
            embedding=embedding.vector,
            metadata={"email_id": "email-dev-007"},
        )
    )

    matches = index.query(embedding.vector, limit=1)

    assert matches[0].id == "email-dev-007"
    assert matches[0].metadata["email_id"] == "email-dev-007"
