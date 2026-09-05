# AI Responsibility Boundaries

## Capability Classification

| Capability | Primary Owner | Why |
| --- | --- | --- |
| Preprocessing | Deterministic code | Normalization, validation, trimming, and metadata handling should be repeatable and testable. |
| Language detection | Deterministic code plus LLM fallback | Lightweight detection can happen during preprocessing; ambiguous cases can be confirmed by the LLM and stored with confidence. |
| Spam/newsletter detection | LLM inference plus deterministic signals | Headers and sender patterns can be deterministic, while content intent may require semantic judgment. |
| Summarization | LLM inference | Condensing varied email content is a natural language generation task. |
| Categorization | LLM inference with configured taxonomy | Semantic interpretation is needed, but the output should be constrained to known categories. |
| Action detection | LLM inference | Determining whether a message asks the user to do something often requires language understanding. |
| Action extraction | LLM inference with schema validation | Extracting tasks, owners, and implied requests benefits from semantic parsing. |
| Deadline extraction | LLM inference plus deterministic date parsing | The LLM can identify candidate date expressions; deterministic parsing should normalize dates where possible. |
| Historical-context lookup | Retrieval/RAG | Searching previous messages should be handled by retrieval, not by asking the LLM to remember context. |
| User-preference lookup | Deterministic code | Preferences are explicit stored configuration and should be loaded predictably. |
| Priority calculation | Deterministic code | Final ranking needs reproducibility, testability, and auditability. |
| Explanation generation | Deterministic construction with optional LLM wording | The explanation should be grounded in stored factors; an LLM may polish wording but must not invent reasons. |
| Tool selection | Agent/orchestrator for V1 routing only | V1 has a small fixed workflow, so a normal orchestrator is enough. An agent is only useful if future tool choice becomes dynamic. |
| Calendar availability lookup | External tool/API | Availability belongs to the calendar provider or a calendar integration. |
| Calendar event proposal | LLM inference plus deterministic validation | The LLM can infer event candidates, while deterministic code validates required fields. |
| Calendar event creation | External tool/API gated by human approval | Actual writes are side effects and must happen only through an isolated tool after approval. |

## LLM Use

The LLM should be used for semantic interpretation and generation where email language is variable:

- Summaries.
- Categories.
- Action-required detection.
- Action item extraction.
- Deadline and meeting candidate extraction.
- Short rationale fields for inferred analysis.
- Interpreting supported non-English emails using the same structured schema.

All LLM outputs consumed by downstream code must be structured and schema-validated. Invalid outputs should not enter priority calculation as trusted facts. User-facing summaries and explanations should be generated in the user's configured output language unless the user later configures source-language display.

## Retrieval Use

Retrieval should provide context, not make decisions. It is appropriate for:

- Prior emails in the same thread.
- Past interactions with the same sender.
- Similar project-related emails.
- Ambiguous references such as "as discussed" or "following up."
- Cases where historical context can affect urgency or interpretation.

Retrieval may be skipped for clear low-value emails, standalone newsletters, spam-like messages, or messages with no useful historical corpus.

## Deterministic Code

Deterministic code should own:

- Validation and preprocessing.
- Initial language detection and locale metadata handling.
- Schema enforcement.
- Preference loading.
- Priority scoring.
- Explanation factor assembly.
- Approval state transitions.
- External write gating.

This keeps core behavior reproducible and testable.

## Agent Evaluation

A full LLM agent is not necessary for V1. The workflow does not require open-ended tool discovery, iterative planning, or autonomous decision-making. A normal orchestration layer can decide when to call retrieval, the LLM analysis service, the priority engine, and the calendar proposal path.

Structured LLM calls are preferable for V1 because they are easier to test, constrain, evaluate, and debug. An agent could become useful in a future version if the system supports many optional tools, complex multi-step scheduling negotiation, or dynamic follow-up workflows. It should not be introduced for simple classification, extraction, or fixed pipeline routing.

## Human Approval

Human approval owns the final decision for side effects. The system may propose calendar events, but it must not create them until the user explicitly approves the specific proposal.
