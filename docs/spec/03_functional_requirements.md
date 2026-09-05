# Functional Requirements

## Requirement Table

### FR-01 Email Ingestion

- Name: Email ingestion
- Description: Import a bounded set of emails into the system for processing.
- Input: Email files, fixture records, or controlled email API results.
- Expected behavior: Capture sender, recipients, subject, body, timestamps, thread identifiers, and provider identifiers when available.
- Output: Raw email records.
- Acceptance condition: A representative test inbox can be loaded without manual record editing.
- V1 priority: Must
- Dependencies: None

### FR-02 Preprocessing And Normalization

- Name: Preprocessing and normalization
- Description: Convert raw email content into a consistent form for downstream analysis.
- Input: Raw email record.
- Expected behavior: Normalize text, remove or mark quoted text/signatures where practical, preserve original source fields, and validate required metadata.
- Output: Processed email base record.
- Acceptance condition: Downstream analysis receives normalized content and required metadata or a structured validation error.
- V1 priority: Must
- Dependencies: FR-01

### FR-03 Low-Value Message Detection

- Name: Low-value message detection
- Description: Detect spam-like, newsletter, automated notification, and low-value messages.
- Input: Normalized email.
- Expected behavior: Assign low-value flags and reason codes. Low-value subtype values are `spam-like`, `newsletter`, `automated_notification`, and `other_low_value`.
- Output: Low-value classification signals.
- Acceptance condition: Test newsletters and automated notifications are separated from action-oriented emails.
- V1 priority: Must
- Dependencies: FR-02

### FR-04 Summarization

- Name: Email summarization
- Description: Produce concise summaries of email content.
- Input: Normalized email text and selected context if available.
- Expected behavior: Generate a short factual summary focused on the sender's intent and user-relevant information.
- Output: Summary text and confidence or quality indicators.
- Acceptance condition: Each successfully analyzed email has a summary or explicit fallback state.
- V1 priority: Must
- Dependencies: FR-02

### FR-05 Categorization

- Name: Email categorization
- Description: Assign a primary user-facing category.
- Input: Normalized email, user preferences, and optional retrieved context.
- Expected behavior: Select one category and provide category rationale.
- Output: Category, optional secondary labels, rationale.
- Acceptance condition: Every analyzed email receives one primary category from the configured taxonomy.
- V1 priority: Must
- Dependencies: FR-02, FR-09, FR-10

### FR-06 Action-Required Detection

- Name: Action-required detection
- Description: Determine whether the user likely needs to respond, decide, complete a task, or attend something.
- Input: Normalized email and optional context.
- Expected behavior: Produce a boolean action-required signal with rationale.
- Output: Action-required flag, confidence, rationale.
- Acceptance condition: Known task/request examples are marked action required while pure informational examples are not.
- V1 priority: Must
- Dependencies: FR-02, FR-09

### FR-07 Action Extraction

- Name: Action extraction
- Description: Extract concrete user actions requested or implied by the email.
- Input: Normalized email and action-required signal.
- Expected behavior: Extract one or more action items with owner, due date, and source text references when available.
- Output: Structured action items.
- Acceptance condition: Emails containing explicit tasks produce structured action records.
- V1 priority: Should
- Dependencies: FR-06

### FR-08 Deadline And Meeting Extraction

- Name: Deadline and meeting extraction
- Description: Extract dates, deadlines, meeting times, attendees, and scheduling details.
- Input: Normalized email.
- Expected behavior: Produce structured deadline and meeting candidates with uncertainty when incomplete.
- Output: Deadline records and meeting detail records.
- Acceptance condition: Fixture emails with dates and meetings produce parseable structured fields.
- V1 priority: Must
- Dependencies: FR-02

### FR-09 Historical Context Retrieval

- Name: Historical context retrieval
- Description: Retrieve relevant historical emails or thread context when useful for understanding the current email.
- Input: Current email, thread metadata, sender, subject, embeddings, and retrieval trigger signals.
- Expected behavior: Return top relevant context snippets with source identifiers or skip retrieval with a recorded reason. Retrieval results must exclude the current email ID.
- Output: Retrieved context records.
- Acceptance condition: At least one labeled fixture pair identifies expected related source email IDs and shows historical context influencing analysis or priority.
- V1 priority: Must
- Dependencies: FR-01, FR-02, FR-13

### FR-10 User Preference Retrieval

- Name: User preference retrieval
- Description: Load user-specific sender, category, keyword, and priority preferences.
- Input: User profile identifier or local configuration.
- Expected behavior: Return active preferences for priority and display decisions.
- Output: User preference set.
- Acceptance condition: Configured preferences affect at least one demonstrated priority result.
- V1 priority: Must
- Dependencies: None

### FR-11 Priority Calculation

- Name: Priority calculation
- Description: Calculate final email priority using deterministic logic over analysis signals, retrieved context, and preferences.
- Input: Analysis signals, low-value flags, deadlines, context, and user preferences.
- Expected behavior: Produce a priority score, priority band, and contributing factor list.
- Output: Priority result.
- Acceptance condition: Priority can be recalculated and explained without re-running the LLM.
- V1 priority: Must
- Dependencies: FR-03, FR-06, FR-08, FR-09, FR-10

### FR-12 Decision Explanation

- Name: Decision explanation
- Description: Build a user-readable explanation for category and priority decisions.
- Input: Analysis signals, priority factors, retrieved context summaries, and preferences used.
- Expected behavior: Explain the most important reasons without exposing unnecessary prompt internals.
- Output: Explanation text and factor list.
- Acceptance condition: Every high-priority result has stored contributing factors and user-facing rationale.
- V1 priority: Must
- Dependencies: FR-05, FR-11

### FR-13 Persistence Of Analysis Results

- Name: Persistence of analysis results
- Description: Store raw email references, normalized records, analysis outputs, retrieved context, priority results, and approval states.
- Input: Records produced across the pipeline.
- Expected behavior: Persist enough data to reload the UI and audit final decisions.
- Output: Durable stored analysis state.
- Acceptance condition: Restarting the app does not lose completed analysis for the test inbox.
- V1 priority: Must
- Dependencies: FR-01 through FR-12 as applicable

### FR-14 UI Presentation

- Name: UI presentation
- Description: Present a simple usable interface for reviewing prioritized emails and analysis details.
- Input: Persisted email analysis records.
- Expected behavior: Show priority, summary, category, action status, deadline/meeting indicators, explanation, context, and calendar proposal state.
- Output: User-visible triage UI.
- Acceptance condition: A user can identify the top-priority emails and inspect why each was ranked.
- V1 priority: Must
- Dependencies: FR-13

### FR-15 Calendar Action Proposal

- Name: Calendar action proposal
- Description: Create a proposed calendar event when extracted meeting or deadline data is sufficient.
- Input: Deadline or meeting extraction results and source email.
- Expected behavior: Generate a proposed event with title, time, participants, source, confidence, and missing fields.
- Output: Calendar event proposal.
- Acceptance condition: Meeting-like emails produce proposals and incomplete emails do not trigger writes.
- V1 priority: Must
- Dependencies: FR-08, FR-13

### FR-16 Approval Before External Write

- Name: Approval before external write
- Description: Require explicit user approval before performing any external calendar write.
- Input: Calendar event proposal and user approval/rejection action.
- Expected behavior: Store approval decision and allow execution only after approval.
- Output: Tool approval record.
- Acceptance condition: No test path can call the calendar write operation without an approved proposal.
- V1 priority: Must
- Dependencies: FR-15

### FR-17 Calendar API Execution

- Name: Calendar API execution
- Description: Write approved calendar events through an isolated calendar API integration.
- Input: Approved calendar event proposal.
- Expected behavior: Call external API, record success/failure, and persist provider event identifier when successful. Execution must be idempotent per proposal ID and must not create duplicate events on retry.
- Output: Calendar write result.
- Acceptance condition: An approved test proposal can create a calendar event in a sandbox or mocked integration.
- V1 priority: Should
- Dependencies: FR-16

### FR-18 Multilingual Email Handling

- Name: Multilingual email handling
- Description: Detect the email language and process supported non-English emails through the same structured triage pipeline.
- Input: Normalized email text, detected or provided language metadata, user output-language preference, and locale configuration.
- Expected behavior: Store detected language, analyze the email using the standard schema, generate user-facing summaries and explanations in the configured output language, and normalize dates where possible using language and locale cues.
- Output: Language metadata, structured analysis signals, translated or output-language-aligned summary/explanation, and normalized date/meeting fields with uncertainty when needed.
- Acceptance condition: The evaluation fixture set includes at least two non-English emails, including one with an action item and one with a date or meeting reference, and both are processed end-to-end with valid schema output.
- V1 priority: Must
- Dependencies: FR-02, FR-04, FR-05, FR-06, FR-08, FR-10, FR-12

## Requirement Ownership

| Requirement | Owner component |
|---|---|
| FR-01 | Email Ingestion Service |
| FR-02 | Preprocessing Service |
| FR-03 | LLM Analysis Service |
| FR-04 | LLM Analysis Service |
| FR-05 | LLM Analysis Service |
| FR-06 | LLM Analysis Service |
| FR-07 | LLM Analysis Service |
| FR-08 | LLM Analysis Service |
| FR-09 | Retrieval/RAG Service |
| FR-10 | User Preference Service |
| FR-11 | Priority Engine |
| FR-12 | Priority Engine with optional LLM wording support |
| FR-13 | Persistence Layer |
| FR-14 | UI and API/Backend |
| FR-15 | Calendar Proposal Logic |
| FR-16 | Approval Service and API/Backend |
| FR-17 | Calendar Tool Service |
| FR-18 | Preprocessing Service, LLM Analysis Service, and User Preference Service |

## Dependency Summary

FR-01 and FR-10 are foundational. FR-02 depends on ingestion. FR-03 through FR-08 analyze normalized email data. FR-09 depends on stored or indexed prior email data. FR-11 combines analysis, retrieval, and preferences. FR-12 explains FR-11 and FR-05. FR-13 persists all major records. FR-14 reads persisted results. FR-15 through FR-17 isolate calendar proposal, approval, and external write execution. FR-18 extends the same analysis requirements to supported non-English fixture emails and depends on preprocessing, analysis, preferences, and explanation behavior.
