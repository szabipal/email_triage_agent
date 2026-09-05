# Step 6 — Define the Component Architecture

## Prompt

Using the requirements and domain model, design the V1 component architecture for the email triage system.

Define components by responsibility rather than by framework.

At minimum evaluate the need for:

- Email ingestion service
- Preprocessing service
- Embedding/indexing service
- Retrieval/RAG service
- LLM analysis service
- User preference service
- Priority engine
- Persistence layer
- Triage/orchestration layer
- Calendar tool service
- Approval service
- API/backend
- UI

For each component provide:

1. Responsibility
2. Inputs
3. Outputs
4. Dependencies
5. What it explicitly must NOT do
6. Expected failure modes
7. How it can be tested independently

Follow these architectural principles:

- LLMs should perform semantic interpretation and generation.
- Retrieval should provide context rather than make final decisions.
- Deterministic business logic should remain outside the LLM where practical.
- External side effects should be isolated behind explicit tools/services.
- V1 should use a single orchestration layer rather than unnecessary multi-agent architecture.

Provide a high-level component diagram in Mermaid.
