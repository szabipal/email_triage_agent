# Domain And Data Model

This document defines conceptual entities only. It does not prescribe database tables, ORM models, storage engines, or framework classes.

## Email

- Purpose: Preserve facts originating from the email source.
- Required fields: `id` string, `provider_message_id` string, `subject` string, `sender` email identity, `recipients` list, `received_at` datetime, `body_raw` text, `source` enum.
- Optional fields: `cc`, `bcc`, `reply_to`, `thread_id`, `headers`, `attachments_metadata`, `labels`.
- Relationships: May belong to one `EmailThread`; has one `ProcessedEmail`; may have one `EmailAnalysis`.
- Invariants: Raw fields must not be overwritten by inferred fields; source identifiers should remain stable.
- Undecided: Exact attachment handling and provider-specific metadata shape.

## ProcessedEmail

- Purpose: Store normalized content prepared for analysis.
- Required fields: `id` string, `email_id` string, `normalized_subject` string, `normalized_body` text, `processed_at` datetime, `status` enum.
- Optional fields: `body_without_quotes`, `signature_removed` boolean, `detected_language`, `language_confidence`, `locale_hint`, `processing_errors`.
- Relationships: Derived from one `Email`; consumed by analysis and retrieval.
- Invariants: Must retain a link to the original email; normalization must not delete the original raw body.
- Undecided: Exact quote and signature removal strategy.

## EmailThread

- Purpose: Group related emails for thread-aware context.
- Required fields: `id` string, `subject_key` string, `email_ids` list.
- Optional fields: `provider_thread_id`, `participants`, `first_seen_at`, `last_seen_at`, `summary`.
- Relationships: Contains many `Email` records; can be used by `RetrievedContext`.
- Invariants: Thread grouping should be explainable by provider ID or deterministic subject/participant matching.
- Undecided: Whether thread summaries are generated and persisted in V1.

## RetrievedContext

- Purpose: Represent historical context retrieved through RAG or thread lookup.
- Required fields: `id` string, `source_email_ids` list, `query_email_id` string, `retrieval_method` enum, `summary` text, `relevance_score` number.
- Optional fields: `snippet_text`, `rank`, `embedding_model`, `retrieval_query`, `skip_reason`.
- Relationships: Used by `EmailAnalysis` and may influence `PriorityResult`.
- Invariants: Must distinguish retrieved information from facts in the current email; should cite source email IDs; any context used in priority factors must preserve source IDs and either stable snippet text or a stable persisted source reference.
- Undecided: Exact scoring scale and embedding metadata.

## UserPreference

- Purpose: Store user-specific configuration that affects priority and display.
- Required fields: `id` string, `preference_type` enum, `value` string or structured value, `effect` enum, `weight` number, `enabled` boolean.
- Optional fields: `description`, `created_at`, `updated_at`, `expires_at`.
- Relationships: Used by `PriorityResult`, `EmailAnalysis`, and UI configuration.
- Invariants: Preferences must be explicit and auditable when they affect priority.
- Undecided: Exact UI for preference editing.

Language-related preferences should include the user's configured interface/output language and optional locale/timezone defaults for date interpretation.

## EmailAnalysisSignals

- Purpose: Store structured LLM-inferred signals before deterministic priority calculation.
- Required fields: `id` string, `processed_email_id` string, `summary` text, `category` string, `action_required` boolean, `low_value_type` enum or null, `confidence` number.
- Optional fields: `action_items`, `deadlines`, `meeting_details`, `semantic_flags`, `source_language`, `output_language`, `translation_notes`, `model_name`, `prompt_version`, `schema_version`.
- Relationships: Input to `PriorityResult`; part of `EmailAnalysis`.
- Invariants: Must be schema-validated before use; must not contain final deterministic priority as an LLM-only decision.
- Undecided: Exact confidence calibration.

## PriorityResult

- Purpose: Store deterministic priority score and rationale factors.
- Required fields: `id` string, `email_id` string, `score` number, `band` enum, `factors` list, `calculated_at` datetime, `ruleset_version` string.
- Optional fields: `preference_matches`, `context_influence`, `deadline_urgency`, `low_value_penalty`, `recalculated_from_id`.
- Relationships: Depends on `EmailAnalysisSignals`, `RetrievedContext`, and `UserPreference`.
- Invariants: Must be reconstructable without re-running the LLM; every score should list positive and negative factors.
- Undecided: Exact score range and band thresholds.

Urgency is one priority factor derived from deadlines, meeting times, and recency. It is not a separate final ranking.

## EmailAnalysis

- Purpose: Aggregate the final analysis state for one email.
- Required fields: `id` string, `email_id` string, `processed_email_id` string, `signals_id` string, `priority_result_id` string, `status` enum.
- Optional fields: `retrieved_context_ids`, `calendar_proposal_ids`, `explanation`, `errors`, `completed_at`.
- Relationships: Connects current email facts, inferred signals, context, priority, and proposed actions.
- Invariants: A completed analysis must reference validated signals and a priority result.
- Undecided: Whether partial analyses are visible in the V1 UI.

## ProposedAction

- Purpose: Represent non-calendar actions extracted from an email.
- Required fields: `id` string, `email_id` string, `description` text, `action_type` enum, `source` enum.
- Optional fields: `owner`, `due_at`, `confidence`, `source_excerpt`, `status`.
- Relationships: Derived from `EmailAnalysisSignals`; may be displayed in UI.
- Invariants: Proposed actions are suggestions, not autonomous actions. A `CalendarEventProposal` is not stored as a `ProposedAction` unless it is separately shown as a non-side-effect task.
- Undecided: Whether user completion tracking belongs in V1.

## CalendarEventProposal

- Purpose: Represent a proposed calendar event before any external write.
- Required fields: `id` string, `email_id` string, `title` string, `start_at` datetime or partial datetime, `status` enum, `source` enum.
- Optional fields: `end_at`, `timezone`, `location`, `attendees`, `description`, `confidence`, `missing_fields`, `locale_assumption`, `time_ambiguity`, `provider_event_id`.
- Relationships: May require one `ToolApproval`; executed by calendar service only after approval.
- Invariants: A proposal is not a calendar event until approved and successfully written. Valid status values are `pending`, `incomplete`, `approved`, `rejected`, `expired`, `executing`, `executed`, and `failed`. Rejected, expired, and executed proposals must not be executed.
- Undecided: How partial dates and timezone ambiguity are represented.

## ToolApproval

- Purpose: Record explicit user approval or rejection for external side effects.
- Required fields: `id` string, `proposal_id` string, `tool_name` string, `decision` enum, `decided_at` datetime, `decided_by` string.
- Optional fields: `approval_notes`, `execution_status`, `execution_error`, `external_result_id`.
- Relationships: Gates `CalendarEventProposal` execution.
- Invariants: External writes require an approved decision; rejected or pending proposals must not execute. For V1, `ToolApproval` execution fields plus `CalendarEventProposal` provider fields form the canonical execution audit trail.
- Undecided: Whether approval audit includes UI session metadata in V1.

## Separation Of Information Types

- Email facts: `Email`, source-linked fields in `ProcessedEmail`.
- LLM inference: `EmailAnalysisSignals`, extracted action candidates, extracted meeting/deadline candidates, summaries, categories, language-aware interpretation.
- Retrieved context: `RetrievedContext` with source email IDs and retrieval metadata.
- Deterministic calculations: `PriorityResult`.
- User preferences: `UserPreference`, including output language and locale defaults.
- External actions: `CalendarEventProposal` and `ToolApproval`.

`EmailAnalysisSignals` owns extracted candidates. `CalendarEventProposal` owns validated user-facing event proposal data and the lifecycle leading to optional external execution.

Auditability requires `EmailAnalysis` to connect all of these records so the system can reconstruct why an email received its final priority.
