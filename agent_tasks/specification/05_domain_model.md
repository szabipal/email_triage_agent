# Step 5 — Define the Domain and Data Models

## Prompt

Design the conceptual data model for the email triage system.

Do not implement database models or framework-specific classes yet.

Define the minimum domain entities required for V1.

At minimum consider:

- Email
- ProcessedEmail
- EmailThread
- RetrievedContext
- UserPreference
- EmailAnalysisSignals
- PriorityResult
- EmailAnalysis
- ProposedAction
- CalendarEventProposal
- ToolApproval

For each entity define:

- purpose
- required fields
- optional fields
- field type conceptually
- relationships to other entities
- invariants/constraints

Pay particular attention to separating:

1. facts originating from the email
2. information inferred by the LLM
3. information retrieved through RAG
4. deterministic priority calculations
5. user preferences
6. external actions

The design should support auditability: it should be possible to reconstruct why an email received its final priority.

Flag any fields whose exact design should remain undecided until implementation.
