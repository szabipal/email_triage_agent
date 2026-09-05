# Email Triage System Scope

## Project Objective

Build a portfolio-scale AI email triage system that helps a single user spend less manual attention managing an inbox by summarizing, classifying, prioritizing, and surfacing emails that need action.

V1 should demonstrate practical AI system design: structured LLM output, retrieval-augmented context, deterministic priority logic, explainable results, human approval for side effects, persistence, a simple UI, and an external calendar write path.

## Primary User

The primary user is an individual knowledge worker who receives enough email that manual scanning is costly, but who still needs final control over important decisions and external actions.

## Core Problem

Inbox attention is expensive because important emails, deadlines, meeting requests, and action items are mixed with newsletters, spam, automated notifications, and low-value messages. The system should reduce scanning effort by showing a smaller, clearer, prioritized view with concise reasoning.

## Canonical Terminology

- Email: The original source message and its provider metadata.
- ProcessedEmail: The normalized representation prepared for analysis while preserving a link to the original Email.
- RetrievedContext: The canonical persisted entity for prior-email evidence used during analysis. Historical context is the source material from prior emails or threads; RAG is one retrieval method that can produce RetrievedContext.
- Low-value message: An analysis signal with one optional subtype: spam-like, newsletter, automated notification, or other low-value. It is not the same as the primary user-facing category.
- Urgency: A priority factor derived from time sensitivity, deadlines, meeting times, or recency. Priority is the final deterministic score and band.
- ProposedAction: A non-side-effect suggested task extracted from an email.
- CalendarEventProposal: A specific external-action proposal that may require ToolApproval before calendar execution.
- Orchestrator: Deterministic workflow coordination for V1. It is not a multi-agent system.

## In-Scope V1 Capabilities

- Ingest a bounded test inbox or imported email dataset.
- Normalize email metadata and body content for analysis.
- Detect likely spam, newsletters, automated notifications, and low-value messages.
- Generate concise summaries.
- Categorize emails into user-facing categories.
- Detect email language and process a small set of non-English emails using the same analysis pipeline.
- Detect whether an email requires action.
- Extract action items, deadlines, meeting details, and calendar-relevant information.
- Retrieve relevant historical email context when useful.
- Apply user-specific preferences for important senders, categories, keywords, and priority rules.
- Calculate a final priority using deterministic logic informed by extracted signals, retrieved context, and preferences.
- Store analysis results and contributing factors for auditability.
- Explain why a category and priority were assigned.
- Present a simple UI showing the prioritized inbox and analysis details.
- Propose calendar actions when an email appears to contain a meeting or deadline.
- Require explicit user approval before writing to an external calendar API.
- Execute approved calendar writes through an isolated external API integration.

## Explicit Non-Goals For V1

- Automatic email sending.
- Autonomous deletion or archiving.
- Complex multi-agent architecture.
- Slack integration.
- Voice interface.
- Knowledge graphs.
- Fine-tuning custom models.
- Full production authentication system.
- Automatic continuous inbox monitoring.
- Enterprise-grade multi-user SaaS behavior.
- Real-time push notification infrastructure.
- Automatic response drafting beyond optional future exploration.
- Full email client replacement.

## Assumptions

- V1 can run locally using documented setup steps.
- V1 can use a fixed test inbox, exported email files, or a controlled email API sandbox.
- The system is designed around one user profile.
- The user has one configured interface/output language for summaries and explanations.
- Calendar integration can use a sandbox or developer account.
- Real credentials and real email contents are excluded from the repository.
- The LLM returns structured outputs that downstream code validates before use.
- The selected LLM is capable of handling the non-English fixture languages chosen for V1 evaluation.
- Retrieval is used selectively, especially for threads, recurring senders, repeated projects, or ambiguous context.
- Final priority is not delegated entirely to the LLM.

## High-Level Success Criteria

- A developer can run the project locally and process a representative test inbox.
- The system displays a reduced, prioritized inbox with summaries, categories, action indicators, deadlines, and explanations.
- The system can correctly process at least two non-English fixture emails, including one action-oriented message and one date or meeting example.
- Low-value emails are clearly separated from emails that need user attention.
- At least one demonstrated result changes because of retrieved historical context.
- At least one demonstrated result changes because of user preferences.
- Every final priority decision can be reconstructed from stored factors.
- Calendar events are proposed when appropriate.
- No calendar write occurs without explicit user approval.
- Automated tests and an evaluation script verify core behavior.
