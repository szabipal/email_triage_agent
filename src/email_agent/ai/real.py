from __future__ import annotations

import json
from http import HTTPStatus
from typing import Any, cast
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

from email_agent.ai.provider import LLMError, LLMRequest, LLMResponse


class OpenAILLMProvider:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.openai.com/v1/responses",
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url

    def complete_structured(self, request: LLMRequest) -> LLMResponse:
        payload = json.dumps(
            {
                "model": request.model,
                "input": request.prompt,
                "text": {
                    "format": {
                        "type": "json_schema",
                        "name": request.schema_name,
                        "schema": request.json_schema,
                    }
                },
            }
        ).encode()
        http_request = urlrequest.Request(
            self.base_url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlrequest.urlopen(
                http_request,
                timeout=request.timeout_seconds,
            ) as response:
                body = json.loads(response.read())
        except HTTPError as error:
            if error.code == HTTPStatus.TOO_MANY_REQUESTS:
                raise LLMError("rate_limited") from error
            raise LLMError(f"provider_http_{error.code}") from error
        except TimeoutError:
            raise
        except URLError as error:
            raise LLMError("provider_unavailable") from error

        return LLMResponse(
            output=_extract_json_object(body),
            model_name=request.model,
            prompt_version=request.prompt_version,
            schema_version=request.schema_name,
            **_usage_fields(body),
        )


def _extract_json_object(body: Any) -> dict[str, object]:
    if isinstance(body, dict) and isinstance(body.get("output_text"), str):
        return cast(dict[str, object], json.loads(body["output_text"]))

    if isinstance(body, dict):
        for item in body.get("output", []):
            for content in item.get("content", []):
                text = content.get("text")
                if isinstance(text, str):
                    return cast(dict[str, object], json.loads(text))

    raise LLMError("OpenAI response did not contain structured JSON text")


def _usage_fields(body: Any) -> dict[str, int]:
    if not isinstance(body, dict) or not isinstance(body.get("usage"), dict):
        return {}
    usage = body["usage"]
    fields = {
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "total_tokens": usage.get("total_tokens"),
    }
    return {key: value for key, value in fields.items() if isinstance(value, int)}
