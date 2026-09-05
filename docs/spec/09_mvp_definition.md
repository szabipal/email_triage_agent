# V1 MVP Definition

This document freezes V1 scope before implementation. It does not introduce new features beyond the prior specification documents.

## Feature Classification

### MUST HAVE FOR V1

- Bounded email ingestion from fixtures, files, or a controlled source.
- Per-email validation and preprocessing.
- Per-email failure isolation.
- Structured LLM analysis with schema validation.
- Language detection and scoped multilingual handling for supported fixture languages.
- Email summaries.
- Primary email category assignment.
- Low-value message detection.
- Action-required detection.
- Deadline and meeting candidate extraction.
- Selective historical-context retrieval using RAG or thread lookup.
- User preference configuration for important senders, categories, keywords, or weights.
- Deterministic priority calculation from explicit factors.
- Stored priority factors and explanations.
- Persistence of raw email references, processed email records, analysis results, retrieved context, priority results, proposals, approvals, and errors.
- Simple UI showing prioritized inbox, summary, category, priority, action status, deadline/meeting indicators, explanation, and context.
- Calendar event proposal for emails with sufficient meeting or deadline details.
- Explicit approve/reject flow for calendar proposals.
- No external calendar write without approval.
- Automated tests for priority rules, schema validation, approval gating, and representative processing behavior.
- Quantitative evaluation for core AI outputs, priority behavior, and scoped multilingual fixtures.
- Documented local setup and run instructions.

### OPTIONAL IF TIME REMAINS

- Preference editing directly in the UI instead of config-only preferences.
- Richer thread summaries.
- Retry controls for failed calendar writes.
- Feedback capture for incorrect summaries, categories, or priorities.
- Improved low-value detection using provider metadata.
- Calendar availability lookup before proposing an event.
- Calendar write execution through a sandbox, mocked provider, or real external API with safe credentials.
- More detailed confidence display.
- Better handling for attachments metadata.
- Broad language coverage beyond the explicitly evaluated fixture languages.
- Full UI localization beyond generated summaries and explanations.

### V2 / FUTURE WORK

- Automatic email sending.
- Autonomous deletion or archiving.
- Continuous inbox monitoring.
- Complex multi-agent architecture.
- Slack integration.
- Voice interface.
- Knowledge graphs.
- Fine-tuned custom models.
- Full production authentication system.
- Multi-user SaaS functionality.
- Automatic reply drafting or sending.
- Advanced learning from user feedback.
- Production deployment, billing, or tenant management.

## V1 Demonstration Requirements

V1 must demonstrate:

- Structured LLM processing through validated analysis schemas.
- Meaningful use of RAG, with at least one example where historical context changes or supports analysis.
- User-specific prioritization, with at least one example where preferences affect ranking.
- Deterministic decision logic for final priority.
- Explainability through stored factors and user-facing explanations.
- External tool use through the calendar proposal/execution port, with faithful mocked/sandboxed execution if provider execution is enabled.
- Calendar execution is a Should for MVP: the required V1 path is proposal plus approval gating, with actual provider execution included if time remains.
- Human approval before external side effects.
- Persistence sufficient to reload analysis after restart.
- API/backend engineering that separates core services from UI.
- A simple usable UI.
- Quantitative evaluation over representative fixture emails.
- Scoped multilingual evaluation covering at least two non-English emails.

## Definition Of Done

The project is done when all of the following are true:

- The system processes a representative test inbox end-to-end.
- Processing one malformed or failing email does not crash processing for the rest of the inbox.
- LLM outputs conform to defined schemas before downstream use.
- Invalid LLM outputs are rejected or handled with a clear error state.
- Every successfully analyzed email has a summary, category, action-required status, and final priority.
- At least two non-English fixture emails are processed end-to-end with valid schema output.
- User-facing summaries and explanations for non-English fixture emails use the configured output language.
- Deadline or meeting extraction works on fixture emails containing explicit time-sensitive content.
- Locale-specific date or meeting examples either normalize correctly or record explicit uncertainty.
- Historical context can affect at least one demonstrated analysis or priority result.
- User preferences affect ranking for at least one demonstrated email.
- Priority is calculated from explicit stored factors.
- High-priority explanations show the main contributing factors.
- The UI displays priority, summary, category, action status, deadline/meeting information, explanation, and retrieved context when available.
- A calendar event can be proposed from an eligible email.
- No calendar event is created without explicit approval.
- If calendar execution is enabled, approved calendar writes execute through the configured sandbox, mock, or external API path.
- Rejected calendar proposals do not trigger writes.
- Analysis results and approval states persist across application restart.
- Tests pass for schema validation, priority calculation, approval gating, and representative workflow behavior.
- An evaluation pipeline runs scenario-based pass/fail checks and reports measurable results for selected AI tasks, including scoped multilingual cases.
- Setup instructions document required dependencies, environment variables, fixture data, and run commands.
- The repository excludes real credentials and real private email contents.
- Another developer can run the project locally from the documented setup.

## Scope Lock

Implementation should optimize for this MVP before adding optional features. If a feature does not support the Definition of Done above, it should be deferred unless it is required to preserve the core architecture.
