# ADR-014: File-Based Evaluation Tracking

## Status
Accepted

## Context
The MVP requires scenario-based pass/fail evaluation plus reported metrics for categorization, low-value detection, actions, deadlines, meetings, summarization, retrieval, priority, preferences, unauthorized writes, and multilingual cases. It must compare LLM-only, LLM plus RAG, and RAG plus preferences plus deterministic scoring. This supports NFR-09, NFR-13, NFR-15, and the MVP evaluation requirement.

## Decision
Use versioned JSONL fixtures, JSON prediction outputs, CSV/Markdown reports, and lightweight run metadata files.

## Alternatives considered
MLflow, Weights & Biases, LangSmith, spreadsheets only, and database-only evaluation storage.

## Consequences
Evaluation remains transparent, reviewable in Git, and easy to run locally. Scenario pass/fail results can include supporting evidence and reported metrics. The trade-off is no hosted dashboard or advanced experiment search.

## Reversal strategy
Import JSONL fixtures and run metadata into an experiment-tracking system later if evaluation volume grows.
