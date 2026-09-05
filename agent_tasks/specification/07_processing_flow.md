# Step 7 — Define the End-to-End Processing Flow

## Prompt

Define the end-to-end processing workflow for a single incoming email.

Describe the sequence from ingestion through final display.

Include:

1. Email ingestion
2. Validation
3. Preprocessing
4. Persistence
5. Embedding/index update if applicable
6. Relevant historical-context retrieval
7. User-preference retrieval
8. LLM structured analysis
9. Priority calculation
10. Explanation construction
11. Result persistence
12. UI presentation
13. Optional calendar proposal
14. User approval
15. Calendar write

For each stage specify:

- input
- operation
- output
- failure behavior
- whether the stage is deterministic, retrieval-based, LLM-based, or external-tool-based

Also identify which stages are mandatory for every email and which should run conditionally.

In particular, do not assume RAG must execute for every email. Explain reasonable conditions under which retrieval can be skipped.

Provide both a numbered workflow and a Mermaid sequence diagram.
