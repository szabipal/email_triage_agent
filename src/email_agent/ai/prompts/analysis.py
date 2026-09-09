from __future__ import annotations

from email_agent.domain import ProcessedEmail

ANALYSIS_VERSION = "analysis-v1"
ANALYSIS_SCHEMA_VERSION = "signals-v1"


def render_analysis_prompt(
    processed_email: ProcessedEmail,
    *,
    output_language: str,
    context: list[str] | None = None,
    max_body_chars: int | None = None,
) -> str:
    context_text = "\n".join(context or [])
    body = _capped_body(processed_email.normalized_body, max_body_chars)
    return (
        "Analyze the email into EmailAnalysisSignals JSON. "
        "Include summary, category, action_required, low_value_type, "
        "action_items, deadlines, meeting_details, confidence, and rationale flags. "
        f"Source language: {processed_email.detected_language or 'unknown'}. "
        f"Output language: {output_language}. "
        f"Subject: {processed_email.normalized_subject}\n"
        f"Body: {body}" + (f"\nContext:\n{context_text}" if context_text else "")
    )


def _capped_body(body: str, max_body_chars: int | None) -> str:
    if max_body_chars is None or len(body) <= max_body_chars:
        return body
    return body[:max_body_chars].rstrip() + "\n[truncated]"
