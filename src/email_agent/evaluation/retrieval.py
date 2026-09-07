from __future__ import annotations

from email_agent.domain import RetrievedContext
from email_agent.evaluation.fixtures import FixtureRecord


def recall_at_k(
    expected_ids: list[str],
    contexts: list[RetrievedContext],
    *,
    k: int,
) -> float:
    if not expected_ids:
        return 1.0
    retrieved = {
        source_id for context in contexts[:k] for source_id in context.source_email_ids
    }
    return len(set(expected_ids) & retrieved) / len(set(expected_ids))


def evaluate_retrieval(
    records: list[FixtureRecord],
    predictions: dict[str, list[RetrievedContext]],
    *,
    k: int = 3,
) -> dict[str, object]:
    scored = [
        recall_at_k(
            record.labels.expected_related_source_email_ids,
            predictions.get(record.id, []),
            k=k,
        )
        for record in records
        if record.labels.retrieval_should_run
    ]
    return {
        f"recall_at_{k}": sum(scored) / len(scored) if scored else 1.0,
        "evaluated_records": len(scored),
    }
