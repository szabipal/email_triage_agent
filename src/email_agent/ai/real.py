from __future__ import annotations

import json
from typing import Any, cast
from urllib import request as urlrequest

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

        with urlrequest.urlopen(
            http_request,
            timeout=request.timeout_seconds,
        ) as response:
            body = json.loads(response.read())

        return LLMResponse(
            output=_extract_json_object(body),
            model_name=request.model,
            prompt_version=request.prompt_version,
            schema_version=request.schema_name,
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
