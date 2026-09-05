# Step 8 — Define AI Responsibility Boundaries

## Prompt

Create an AI responsibility specification for the email triage system.

For every major capability, decide whether it belongs primarily to:

- deterministic code
- LLM inference
- retrieval/RAG
- agent/orchestrator
- external tool/API
- human approval

Capabilities to classify:

- preprocessing
- spam/newsletter detection
- summarization
- categorization
- action detection
- action extraction
- deadline extraction
- historical-context lookup
- user-preference lookup
- priority calculation
- explanation generation
- tool selection
- calendar availability lookup
- calendar event proposal
- calendar event creation

For each decision explain why that mechanism is appropriate.

Explicitly evaluate where an LLM agent is actually necessary and where a normal function or structured LLM call is preferable.

The final architecture should avoid using agents for tasks that do not require tool selection, iterative reasoning, or orchestration.
