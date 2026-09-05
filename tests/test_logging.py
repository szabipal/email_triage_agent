import io
import json
import logging
from typing import Any

from email_agent.logging import (
    configure_logging,
    get_logger,
    log_event,
    processing_context,
)


def read_log_record(stream: io.StringIO) -> dict[str, Any]:
    return json.loads(stream.getvalue())


def test_log_event_emits_json_structured_record() -> None:
    stream = io.StringIO()
    configure_logging(stream=stream)

    logger = get_logger("email_agent.tests")
    log_event(
        logger,
        "email.processed",
        processing_id="run-123",
        email_id="email-456",
        stage="analysis",
        latency_ms=12.5,
        fields={"model": "fake-llm"},
    )

    record = read_log_record(stream)

    assert record["event"] == "email.processed"
    assert record["level"] == "info"
    assert record["logger"] == "email_agent.tests"
    assert record["processing_id"] == "run-123"
    assert record["email_id"] == "email-456"
    assert record["stage"] == "analysis"
    assert record["latency_ms"] == 12.5
    assert record["model"] == "fake-llm"


def test_processing_context_supplies_processing_id() -> None:
    stream = io.StringIO()
    configure_logging(stream=stream)

    logger = get_logger("email_agent.tests")
    with processing_context("run-context"):
        logger.warning(
            "stage failed",
            extra={"event": "email.failed", "email_id": "email-789", "stage": "load"},
        )

    record = read_log_record(stream)

    assert record["event"] == "email.failed"
    assert record["level"] == "warning"
    assert record["processing_id"] == "run-context"
    assert record["email_id"] == "email-789"
    assert record["stage"] == "load"
    assert record["latency_ms"] is None


def test_logging_exception_includes_error_field() -> None:
    stream = io.StringIO()
    configure_logging(stream=stream)

    logger = get_logger("email_agent.tests")
    try:
        raise RuntimeError("boom")
    except RuntimeError:
        log_event(logger, "email.failed", level=logging.ERROR, exc_info=True)

    record = read_log_record(stream)

    assert record["event"] == "email.failed"
    assert record["level"] == "error"
    assert "RuntimeError: boom" in record["error"]
