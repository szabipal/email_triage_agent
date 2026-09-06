from datetime import UTC, datetime

from email_agent.api.schemas import ApiError, InboxItem
from email_agent.domain import PriorityBand


def test_api_error_schema_is_stable() -> None:
    assert ApiError(code="not_found", message="Missing").model_dump() == {
        "code": "not_found",
        "message": "Missing",
    }


def test_inbox_item_schema_carries_ui_fields() -> None:
    item = InboxItem(
        email_id="email-1",
        subject="Review",
        sender="ada@example.com",
        received_at=datetime(2026, 1, 1, tzinfo=UTC),
        summary="Ada asks for review.",
        category="work",
        action_required=True,
        priority_band=PriorityBand.HIGH,
        priority_score=80,
    )

    assert item.priority_band == PriorityBand.HIGH
