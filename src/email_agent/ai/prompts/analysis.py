from __future__ import annotations

from email_agent.domain import ProcessedEmail

ANALYSIS_VERSION = "analysis-v1"
ANALYSIS_SCHEMA_VERSION = "signals-v1"


def render_analysis_prompt(
    processed_email: ProcessedEmail,
    *,
    output_language: str,
) -> str:
    return (
        "Analyze the email into EmailAnalysisSignals JSON. "
        "Include summary, category, action_required, low_value_type, "
        "action_items, deadlines, meeting_details, confidence, and rationale flags. "
        f"Source language: {processed_email.detected_language or 'unknown'}. "
        f"Output language: {output_language}. "
        f"Subject: {processed_email.normalized_subject}\n"
        f"Body: {processed_email.normalized_body}"
    )
