from __future__ import annotations

import contextlib
import contextvars
import json
import logging
import sys
from collections.abc import Iterator, Mapping
from types import TracebackType
from typing import Any, TextIO

JsonValue = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]

_processing_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "processing_id",
    default=None,
)

_STANDARD_LOG_RECORD_FIELDS = frozenset(
    logging.LogRecord(
        name="",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="",
        args=(),
        exc_info=None,
    ).__dict__,
)

_STRUCTURED_FIELDS = frozenset(
    {
        "event",
        "processing_id",
        "email_id",
        "stage",
        "latency_ms",
    }
)


class JsonLogFormatter(logging.Formatter):
    """Format log records as one JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        event = getattr(record, "event", None)
        processing_id = getattr(record, "processing_id", None) or _processing_id.get()

        payload: dict[str, JsonValue] = {
            "event": str(event or record.getMessage()),
            "level": record.levelname.lower(),
            "logger": record.name,
            "processing_id": _coerce_json_value(processing_id),
            "email_id": _coerce_json_value(getattr(record, "email_id", None)),
            "stage": _coerce_json_value(getattr(record, "stage", None)),
            "latency_ms": _coerce_json_value(getattr(record, "latency_ms", None)),
        }

        if record.exc_info:
            payload["error"] = self.formatException(record.exc_info)

        for key, value in _record_extras(record).items():
            payload[key] = _coerce_json_value(value)

        return json.dumps(payload, sort_keys=True)


def configure_logging(
    *,
    level: int | str = logging.INFO,
    stream: TextIO | None = None,
) -> logging.Logger:
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)

    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(JsonLogFormatter())
    root_logger.addHandler(handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


@contextlib.contextmanager
def processing_context(processing_id: str) -> Iterator[None]:
    token = _processing_id.set(processing_id)
    try:
        yield
    finally:
        _processing_id.reset(token)


def log_event(
    logger: logging.Logger,
    event: str,
    *,
    level: int = logging.INFO,
    processing_id: str | None = None,
    email_id: str | None = None,
    stage: str | None = None,
    latency_ms: float | None = None,
    fields: Mapping[str, JsonValue] | None = None,
    exc_info: (
        tuple[type[BaseException], BaseException, TracebackType | None]
        | tuple[None, None, None]
        | bool
    ) = False,
) -> None:
    extra: dict[str, JsonValue] = {
        "event": event,
        "processing_id": processing_id,
        "email_id": email_id,
        "stage": stage,
        "latency_ms": latency_ms,
    }

    if fields:
        extra.update(fields)

    logger.log(level, event, extra=extra, exc_info=exc_info)


def _record_extras(record: logging.LogRecord) -> dict[str, JsonValue]:
    return {
        key: _coerce_json_value(value)
        for key, value in record.__dict__.items()
        if key not in _STANDARD_LOG_RECORD_FIELDS and key not in _STRUCTURED_FIELDS
    }


def _coerce_json_value(value: Any) -> JsonValue:
    if value is None or isinstance(value, str | int | float | bool):
        return value

    if isinstance(value, list):
        return [_coerce_json_value(item) for item in value]

    if isinstance(value, tuple):
        return [_coerce_json_value(item) for item in value]

    if isinstance(value, dict):
        return {str(key): _coerce_json_value(item) for key, item in value.items()}

    return str(value)
