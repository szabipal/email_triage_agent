# User Stories

## Critical V1 Stories

### US-01

As a busy email user, I want to view a reduced and prioritized inbox, so that I can focus first on messages that need attention.

Acceptance criteria:

- Given a test inbox with mixed email types, when analysis completes, then the UI shows emails ordered by final priority.
- Given low-value messages are present, when the inbox is displayed, then they are separated or visually deprioritized.
- Given analysis fails for one email, when the inbox is displayed, then successfully processed emails remain visible.

### US-02

As a busy email user, I want concise summaries for emails, so that I can understand the message without opening the full body.

Acceptance criteria:

- Given a processed email, when it appears in the inbox view, then it includes a short summary.
- Given a long email, when summarized, then the summary captures the main request or information.
- Given an empty or malformed body, when summarized, then the system shows a clear unavailable or fallback state.

### US-03

As a busy email user, I want emails categorized, so that I can scan related messages quickly.

Acceptance criteria:

- Given a processed email, when analysis completes, then it has one primary category.
- Given a category is assigned, when details are shown, then the system includes an explanation for that category.
- Given an email does not fit a specific category, when categorized, then it is assigned a general fallback category.

### US-04

As a busy email user, I want emails that require action identified, so that I know what needs a response or follow-up.

Acceptance criteria:

- Given an email asks the user to perform a task, when analysis completes, then it is marked action required.
- Given an informational newsletter, when analysis completes, then it is not marked action required.
- Given an email is ambiguous, when analysis completes, then the result includes confidence or explanatory factors.

### US-05

As a busy email user, I want deadlines and meeting details identified, so that I do not miss time-sensitive commitments.

Acceptance criteria:

- Given an email includes a deadline, when analysis completes, then the deadline is extracted in a structured form.
- Given an email includes meeting date, time, and attendees, when analysis completes, then those fields are extracted when present.
- Given no deadline or meeting exists, when analysis completes, then no calendar proposal is created.

### US-06

As a busy email user, I want to understand why an email was marked high priority, so that I can trust or correct the triage.

Acceptance criteria:

- Given an email receives high priority, when I open its details, then I see the contributing factors.
- Given user preferences affected the ranking, when details are shown, then that influence is visible.
- Given retrieved historical context affected the ranking, when details are shown, then the relevant context summary is visible.

### US-07

As a busy email user, I want to configure important senders, categories, keywords, and preferences, so that the system reflects my priorities.

Acceptance criteria:

- Given a sender is marked important, when future emails from that sender are analyzed, then that preference can increase priority.
- Given a category is marked low priority, when matching emails are analyzed, then that preference can reduce priority.
- Given preferences are changed, when analysis runs again or priority is recalculated, then updated preferences are applied.

### US-08

As a busy email user, I want to view relevant historical context, so that I can understand why the current email matters.

Acceptance criteria:

- Given a related prior email exists, when context retrieval is useful, then the email details show a concise retrieved context summary.
- Given no relevant context exists, when analysis completes, then the system indicates that no relevant context was used.
- Given retrieval is skipped, when details are shown, then the decision remains explainable through other factors.

### US-09

As a busy email user, I want to receive a proposed calendar event from meeting-like emails, so that scheduling requires less manual entry.

Acceptance criteria:

- Given an email contains meeting details, when analysis completes, then a calendar event proposal is created.
- Given required event fields are missing, when analysis completes, then the proposal is marked incomplete rather than written.
- Given a proposal is shown, when I inspect it, then I can see title, time, participants, source email, and confidence.

### US-10

As a busy email user, I want to approve or reject calendar writes, so that no external calendar change happens without my consent.

Acceptance criteria:

- Given a calendar event proposal exists, when I approve it, then the system attempts the calendar API write.
- Given I reject a proposal, when the decision is saved, then no calendar write occurs.
- Given a calendar write succeeds or fails, when I view the proposal, then the final status is visible.

### US-11

As a busy email user, I want non-English emails processed consistently, so that important messages are not missed because they are written in another language.

Acceptance criteria:

- Given a non-English email in a supported fixture language, when analysis completes, then it receives a summary, category, action-required status, and priority.
- Given the user has configured an interface/output language, when a non-English email is summarized or explained, then the user-facing summary and explanation use that configured language.
- Given a non-English email contains a date or meeting reference, when analysis completes, then the extracted deadline or meeting fields are normalized where possible and uncertainty is recorded when locale ambiguity remains.

## Optional Future Stories

### US-12

As a busy email user, I want to provide feedback on incorrect summaries or priorities, so that the system can improve future behavior.

Acceptance criteria:

- Given an analyzed email, when I mark the result incorrect, then the feedback is stored.
- Given feedback exists, when evaluation runs, then the feedback can be included in review.

### US-13

As a busy email user, I want automatic periodic inbox refreshes, so that triage stays current without manual import.

Acceptance criteria:

- Given monitoring is enabled, when new email arrives, then the system processes it without manual import.
- Given monitoring fails, when the user opens the app, then the failure is visible.

### US-14

As a busy email user, I want draft reply suggestions, so that routine responses are faster.

Acceptance criteria:

- Given an action-required email, when I request a draft, then the system proposes one.
- Given a draft is created, when I review it, then it is not sent automatically.
