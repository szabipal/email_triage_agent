# Step 9 — Freeze the MVP and Define Done

## Prompt

Using all existing specification documents, define the exact V1 MVP for the email triage project.

The purpose is to freeze scope before implementation begins.

For every proposed feature classify it as:

- MUST HAVE FOR V1
- OPTIONAL IF TIME REMAINS
- V2 / FUTURE WORK

The V1 must be sufficient to demonstrate:

- structured LLM processing
- meaningful use of RAG
- user-specific prioritization
- deterministic decision logic
- explainability
- external tool use
- human approval for side effects
- persistence
- API/backend engineering
- simple usable UI
- quantitative evaluation

Then define the project's Definition of Done.

The Definition of Done must contain objectively verifiable conditions such as:

- system processes a test inbox end-to-end
- outputs conform to defined schemas
- historical context can affect at least one demonstrated analysis
- priority is calculated from explicit factors
- user preferences affect ranking
- UI displays required fields
- a calendar event can be proposed
- no calendar event is created without approval
- tests pass
- evaluation pipeline runs
- setup is documented
- project is runnable by another developer

Do not add new features while producing this specification.
