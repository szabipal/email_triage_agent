from pathlib import Path

from email_agent.domain import RetrievalMethod, RetrievedContext
from email_agent.evaluation.retrieval import evaluate_retrieval, recall_at_k
from email_agent.evaluation.validator import validate_fixture_file


def context(source_email_id: str) -> RetrievedContext:
    return RetrievedContext(
        id=f"context-{source_email_id}",
        source_email_ids=[source_email_id],
        query_email_id="email-dev-008",
        retrieval_method=RetrievalMethod.RAG,
        summary="Matched context.",
        relevance_score=0.9,
    )


def test_recall_at_k_scores_expected_retrieved_ids() -> None:
    assert recall_at_k(["email-dev-007"], [context("email-dev-007")], k=1) == 1.0
    assert recall_at_k(["email-dev-007"], [context("email-other")], k=1) == 0.0


def test_evaluate_retrieval_reports_recall_for_labeled_fixture() -> None:
    records = validate_fixture_file(Path("datasets/fixtures/dev.jsonl"))
    target = next(record for record in records if record.id == "fixture-dev-008")

    report = evaluate_retrieval(
        [target],
        {"fixture-dev-008": [context("email-dev-007")]},
        k=1,
    )

    assert report == {"recall_at_1": 1.0, "evaluated_records": 1}
