# Specification Consistency Review

Source reviewed: `docs/spec/01_scope.md` through `docs/spec/09_mvp_definition.md`.

Post-decision update: the user resolved the open decisions by choosing `docs/spec/` as the canonical spec path, making calendar execution a Should for MVP, making scoped multilingual handling a Must for MVP, and using scenario-based pass/fail evaluation plus reported metrics for MVP.

## 1. Executive Assessment

Readiness: Ready.

The specification set is coherent enough to begin implementation planning. The scope, user stories, functional requirements, non-functional requirements, domain model, architecture, workflow, AI boundaries, and MVP definition consistently describe a local, portfolio-scale V1 with structured LLM analysis, selective RAG, deterministic priority calculation, persistence, a simple UI, and approval-gated calendar writes.

The decision-dependent corrections have been applied. The specification is ready for implementation planning, with remaining detailed schemas and technology choices to be handled during the implementation-planning step.

## 2. Terminology Consistency

| Issue ID | Affected documents or sections | Conflicting or ambiguous definitions | Implementation risk | Recommended canonical definition |
|---|---|---|---|---|
| TERM-01 | `01_scope.md` In-Scope, `03_functional_requirements.md` FR-09, `05_domain_model.md` RetrievedContext, `07_processing_flow.md` stage 6 | "Historical context", "retrieved context", "RAG", and "thread context" are used interchangeably. | Implementers may create overlapping retrieval records or unclear UI labels. | Use "RetrievedContext" as the canonical persisted entity. Define historical context as source material from prior emails or threads; RAG as one retrieval method that can produce RetrievedContext. |
| TERM-02 | `03_functional_requirements.md` FR-03, `08_ai_responsibilities.md` capability table | "Low-value message", "spam", "newsletter", and "automated notification" are sometimes category-like and sometimes flag-like. | Priority and categorization may duplicate each other or conflict. | Low-value message is an analysis signal with optional subtype values: spam-like, newsletter, automated notification, other low-value. Category remains the primary user-facing category. |
| TERM-03 | `03_functional_requirements.md` FR-08, FR-11, `05_domain_model.md` PriorityResult, `09_mvp_definition.md` DoD | "Urgency" appears as `deadline_urgency` but is not defined as separate from priority. | Priority scoring may mix time urgency and overall importance inconsistently. | Urgency is one priority factor derived from deadlines, meeting times, and recency. Priority is the final deterministic score and band. |
| TERM-04 | `05_domain_model.md` ProposedAction and CalendarEventProposal, `03_functional_requirements.md` FR-07 and FR-15 | ProposedAction and CalendarEventProposal overlap for meeting/deadline actions. | Calendar proposals could be stored twice or lose their approval path. | ProposedAction is a non-side-effect suggested task. CalendarEventProposal is a specific external-action proposal that may require ToolApproval. |
| TERM-05 | `06_architecture.md` Triage Orchestration Layer, `08_ai_responsibilities.md` Agent Evaluation | "Agent/orchestrator" appears in capability classification, while V1 rejects multi-agent architecture. | A developer may overbuild an agent layer. | Orchestrator is deterministic workflow coordination. No LLM agent is part of V1 unless future tool selection becomes dynamic. |
| TERM-06 | `05_domain_model.md` EmailAnalysisSignals and EmailAnalysis | Analysis signals and email analysis are related but easy to confuse. | Persistence code may store inferred fields in the aggregate only, reducing auditability. | EmailAnalysisSignals stores schema-validated LLM inference. EmailAnalysis is the aggregate record connecting facts, signals, retrieved context, priority, proposals, and errors. |
| TERM-07 | `02_user_stories.md` US-10, `05_domain_model.md` ToolApproval, `06_architecture.md` Approval Service | Approval status names and transitions are not canonical. | Backend, UI, and persistence may disagree about pending, approved, rejected, executed, failed, or duplicate states. | ToolApproval is persistent state recording the user decision. CalendarEventProposal owns proposal lifecycle; execution status must prevent duplicate writes. |

Terms with no major inconsistency: email, processed email, email thread, user preference, priority, approval, and RAG are directionally consistent but need the canonical clarifications above.

## 3. Scope Consistency

The project scope and MVP definition align on the main V1: bounded ingestion, preprocessing, structured LLM analysis, selective retrieval, user preferences, deterministic priority, explainability, persistence, UI, calendar proposal, explicit approval, and external calendar execution.

Missing from MVP: none of the original V1 scope items are entirely absent from `09_mvp_definition.md`.

Included in MVP but excluded by scope: none.

V2 features accidentally appearing as V1 requirements: none are clearly accidental. `03_functional_requirements.md` FR-17 makes calendar API execution "Should", while `09_mvp_definition.md` lists calendar write execution as Must Have. This is a priority mismatch, not a new feature.

Components more complex than V1 requires: no multi-agent system is introduced. The component list is broad but responsibility-based and acceptable for implementation planning.

Unclear Must/Should/Could status: none after the decision update. FR-17 remains Should and calendar execution is optional for MVP; FR-18 is Must and scoped multilingual handling remains required.

## 4. Requirements Completeness

Functional requirements FR-01 through FR-18 each have a unique ID, name, description, input, expected behavior, output, acceptance condition, V1 priority, dependencies, and testable behavior. The requirements are mostly observable and implementable.

Gaps after corrections:

- REQ-06: FR-07 is `Should`, while user stories expect identifying emails that require action and action extraction appears in V1 demonstration through structured LLM processing. This is acceptable because FR-06 action detection is Must and detailed action extraction remains Should.

Non-functional requirements NFR-01 through NFR-14 each have a requirement, reason, and verification method. Verification methods are realistic for portfolio scale.

NFR gaps: none requiring user decision after adding scenario-based pass/fail evaluation and explicit zero unauthorized write verification.

## 5. Cross-Document Traceability Matrix

| User story | Functional requirement | Non-functional constraints | Domain entities | Owning component | Workflow stage | Planned test |
|---|---|---|---|---|---|---|
| US-01 | FR-01, FR-02, FR-03, FR-11, FR-14 | NFR-01, NFR-05, NFR-08, NFR-10 | Email, ProcessedEmail, EmailAnalysisSignals, PriorityResult, EmailAnalysis | Ingestion, Preprocessing, Priority Engine, UI | 1-4, 9, 11-12 | Fixture inbox processing and UI ordering test |
| US-02 | FR-04, FR-13, FR-14 | NFR-06, NFR-09 | ProcessedEmail, EmailAnalysisSignals, EmailAnalysis | LLM Analysis, Persistence, UI | 8, 11-12 | Summary schema and fixture faithfulness eval |
| US-03 | FR-05, FR-12, FR-14 | NFR-06, NFR-09 | EmailAnalysisSignals, EmailAnalysis | LLM Analysis, UI | 8, 10-12 | Category fixture eval |
| US-04 | FR-06, FR-07, FR-11, FR-14 | NFR-06, NFR-09 | EmailAnalysisSignals, ProposedAction, PriorityResult | LLM Analysis, Priority Engine, UI | 8-12 | Action-required and action extraction eval |
| US-05 | FR-08, FR-15, FR-14 | NFR-06, NFR-14 | EmailAnalysisSignals, CalendarEventProposal | LLM Analysis, Calendar Proposal Logic, UI | 8, 12-13 | Deadline and meeting extraction eval |
| US-06 | FR-11, FR-12, FR-13, FR-14 | NFR-02, NFR-09 | PriorityResult, RetrievedContext, UserPreference, EmailAnalysis | Priority Engine, Persistence, UI | 9-12 | Priority factor reconstruction test |
| US-07 | FR-10, FR-11, FR-14 | NFR-02, NFR-11 | UserPreference, PriorityResult | User Preference Service, Priority Engine, UI | 7, 9, 12 | Preference influence ranking test |
| US-08 | FR-09, FR-12, FR-14 | NFR-02, NFR-09 | RetrievedContext, EmailAnalysis | Retrieval/RAG Service, LLM Analysis, UI | 6, 8, 10-12 | Related-message retrieval fixture test |
| US-09 | FR-08, FR-15, FR-16 | NFR-03, NFR-06 | CalendarEventProposal, ToolApproval | LLM Analysis, Calendar Proposal Logic, Approval Service | 8, 13-14 | Calendar proposal completeness test |
| US-10 | FR-16, FR-17 | NFR-03, NFR-04 | CalendarEventProposal, ToolApproval | Approval Service, Calendar Tool Service, API/Backend | 14-15 | Approval gating and calendar write test |
| US-11 | FR-18, FR-04, FR-05, FR-06, FR-08, FR-12 | NFR-06, NFR-13, NFR-14 | ProcessedEmail, EmailAnalysisSignals, CalendarEventProposal | Preprocessing, LLM Analysis, User Preference Service | 3, 7-8, 13 | Non-English fixture eval |
| Must FR-01 | FR-01 | NFR-01, NFR-05 | Email | Email Ingestion Service | 1 | Fixture import test |
| Must FR-02 | FR-02 | NFR-01 | ProcessedEmail | Preprocessing Service | 2-3 | Normalization and malformed input test |
| Must FR-03 | FR-03 | NFR-06, NFR-09 | EmailAnalysisSignals | LLM Analysis Service | 8 | Low-value fixture eval |
| Must FR-04 | FR-04 | NFR-06, NFR-09 | EmailAnalysisSignals | LLM Analysis Service | 8 | Summary eval |
| Must FR-05 | FR-05 | NFR-06, NFR-09 | EmailAnalysisSignals | LLM Analysis Service | 8 | Category eval |
| Must FR-06 | FR-06 | NFR-06, NFR-09 | EmailAnalysisSignals | LLM Analysis Service | 8 | Action-required eval |
| Must FR-08 | FR-08 | NFR-06, NFR-14 | EmailAnalysisSignals, CalendarEventProposal | LLM Analysis Service | 8, 13 | Deadline/meeting eval |
| Must FR-09 | FR-09 | NFR-02, NFR-09 | RetrievedContext | Retrieval/RAG Service | 6 | Retrieval influence test |
| Must FR-10 | FR-10 | NFR-11 | UserPreference | User Preference Service | 7 | Preference load test |
| Must FR-11 | FR-11 | NFR-02, NFR-09 | PriorityResult | Priority Engine | 9 | Priority table tests |
| Must FR-12 | FR-12 | NFR-02 | PriorityResult, EmailAnalysis | Priority Engine, LLM Analysis optional wording | 10 | Explanation reconstruction test |
| Must FR-13 | FR-13 | NFR-02, NFR-05 | EmailAnalysis and related records | Persistence Layer | 4, 11 | Restart persistence test |
| Must FR-14 | FR-14 | NFR-10 | EmailAnalysis | UI, API/Backend | 12 | UI display test |
| Must FR-15 | FR-15 | NFR-03, NFR-14 | CalendarEventProposal | Calendar Proposal Logic | 13 | Proposal generation test |
| Must FR-16 | FR-16 | NFR-03 | ToolApproval | Approval Service, API/Backend | 14 | No-write-without-approval test |

GAP: FR-07 and FR-17 are Should requirements, so they are mapped through user stories but not required by the matrix rule for Must requirements. FR-18 is now Must and appears in the matrix through US-11.

## 6. Domain-Model Consistency

The domain model can represent the main pipeline data: original email facts, processed content, retrieved evidence, LLM-inferred signals, user preferences, deterministic priority results, proposed calendar actions, human approvals, and calendar execution result fields.

Separation checks:

- Original facts: represented by Email.
- Preprocessed content: represented by ProcessedEmail.
- Retrieved evidence: represented by RetrievedContext.
- LLM-inferred signals: represented by EmailAnalysisSignals and ProposedAction.
- User preferences: represented by UserPreference.
- Deterministic priority: represented by PriorityResult.
- Proposed external actions: represented by CalendarEventProposal.
- Human approvals: represented by ToolApproval.
- Executed external actions: partially represented by CalendarEventProposal `provider_event_id` and ToolApproval execution fields.

Issues:

- DM-01: Resolved by defining ToolApproval execution fields plus CalendarEventProposal provider fields as the V1 execution audit trail.
- DM-02: Resolved by requiring stable source IDs and snippet or source references for RetrievedContext used in priority factors.
- DM-03: Resolved by clarifying that signals contain extracted candidates and proposals contain validated user-facing event data.
- DM-04: UserPreference can store language and locale defaults, but the exact preference types are not enumerated. This is acceptable for conceptual modeling but should be specified before implementation.

The system can reconstruct why an email received its final priority if PriorityResult factors preserve references to EmailAnalysisSignals, RetrievedContext IDs, and UserPreference IDs. That reference requirement is implied, but should be made explicit.

## 7. Architecture And Workflow Consistency

Every component has a clear responsibility in `06_architecture.md`, and the workflow in `07_processing_flow.md` aligns with those components. Mandatory and conditional stages are distinguished, and RAG is explicitly conditional. Deterministic priority calculation remains outside the LLM. External actions are isolated through Approval Service and Calendar Tool Service.

Issues:

- ARCH-01: Resolved by adding a Calendar Proposal Logic component section.
- ARCH-02: Resolved by routing UI approval through API/backend in the workflow sequence.
- ARCH-03: Resolved by requiring retrieval results to exclude the current email ID.
- ARCH-04: Component interfaces are described as inputs/outputs but not as canonical record contracts. This is fine for the spec phase, but implementation planning should derive explicit schemas.

No unnecessary multi-agent architecture has been introduced.

## 8. Safety And Approval Audit

Calendar path:

1. LLM structured analysis extracts meeting or deadline candidates.
2. Calendar proposal logic creates CalendarEventProposal when enough information exists.
3. UI displays the proposal.
4. User approves or rejects.
5. Approval Service persists ToolApproval.
6. Calendar Tool Service executes only approved proposals.
7. Persistence stores execution success/failure and provider event ID.

Safety findings:

- SAF-01: The LLM can propose but cannot directly execute a write. This is clear.
- SAF-02: Approval is represented as persistent state. This is clear.
- SAF-03: Backend enforcement is specified in architecture text, but the sequence diagram could be read as UI directly calling Approval Service.
- SAF-04: Resolved by defining proposal lifecycle states and disallowed execution states.
- SAF-05: Resolved by requiring idempotent execution keyed by proposal ID.
- SAF-06: Resolved by requiring unauthorized external writes to remain at zero.
- SAF-07: Credentials and real email contents are protected by NFR-04.

Blocking bypass: no direct approval bypass is specified, and retry/idempotency behavior is now specified for V1.

## 9. Evaluation Coverage

| AI capability | Expected ground-truth field | Metric | Target | Evaluation dataset requirement | Missing evaluation decision |
|---|---|---|---|---|---|
| Categorization | Expected primary category | Accuracy or exact match | GAP | Fixture emails with labels | Target threshold |
| Low-value detection | Expected low-value flag/subtype | Precision/recall or confusion matrix | GAP | Newsletters, spam-like, notifications, normal mail | Target threshold and subtype policy |
| Action-required detection | Expected action_required boolean | Precision/recall | GAP | Requests and informational emails | Target threshold |
| Action extraction | Expected action item list | Field-level match or rubric score | GAP | Emails with explicit tasks | Match policy for partial extraction |
| Deadline extraction | Expected normalized deadline fields | Field-level exact/partial match | GAP | Emails with explicit and ambiguous dates | Target threshold and ambiguity scoring |
| Meeting detection | Expected meeting candidate fields | Field-level match | GAP | Meeting request fixtures | Target threshold |
| Summarization faithfulness | Human reference or rubric labels | Rubric score | GAP | Emails with reference summaries | Rubric and pass threshold |
| Historical-context retrieval | Expected related email IDs | Recall@k or hit rate | GAP | Thread/sender/project fixture pairs | k value and pass threshold |
| Priority ranking | Expected rank order or priority band | Rank correlation, band accuracy, or scenario pass/fail | GAP | Mixed inbox with expected priority outcomes | Metric and target |
| User-preference adherence | Expected priority change from preference | Scenario pass/fail | GAP | Preference-sensitive fixture pairs | Number of required scenarios |
| Unauthorized external writes | Expected zero writes without approval | Count of unauthorized writes | Zero implied by NFR-03 | Approval-gating test fixtures | Explicit target should be stated as 0 |

The specs require scenario-based pass/fail evaluation plus reported metrics for MVP. Strict numeric model-quality thresholds are intentionally deferred.

## 10. Issue Register

| Issue ID | Severity | Source documents | Problem | Consequence | Recommended resolution | User decision required? |
|---|---|---|---|---|---|---|
| PATH-01 | Minor | Pasted task, workspace files | Resolved: canonical specs now live in `docs/spec/...`. | Future prompts can use stable paths. | No further correction required. | No |
| SCOPE-01 | Major | `03_functional_requirements.md` FR-17, `09_mvp_definition.md` Must Have | Resolved: calendar API execution is Should for MVP. | Proposal and approval remain required; execution is optional if time remains. | No further correction required. | No |
| SCOPE-02 | Major | `03_functional_requirements.md` FR-18, `09_mvp_definition.md` Must Have | Resolved: multilingual handling is Must for MVP. | V1 requires scoped non-English fixture coverage. | No further correction required. | No |
| TERM-01 | Minor | `01_scope.md`, `03_functional_requirements.md`, `05_domain_model.md`, `07_processing_flow.md` | Historical context, retrieved context, RAG, and thread context need canonical definitions. | Retrieval interfaces may diverge. | Add terminology definitions to the spec set. | No |
| TERM-02 | Minor | `03_functional_requirements.md`, `08_ai_responsibilities.md` | Low-value, spam, newsletter, and notification are not clearly flag versus category. | Classification duplication. | Define low-value as signal with subtype. | No |
| TERM-03 | Minor | `05_domain_model.md`, `09_mvp_definition.md` | Urgency is not defined relative to priority. | Priority scoring ambiguity. | Define urgency as one priority factor. | No |
| TERM-04 | Minor | `03_functional_requirements.md`, `05_domain_model.md` | ProposedAction and CalendarEventProposal overlap. | Duplicate action storage. | Define ProposedAction as non-side-effect task; CalendarEventProposal as external-action proposal. | No |
| REQ-01 | Minor | `03_functional_requirements.md`, `06_architecture.md` | Resolved: functional requirement ownership table added. | Traceability no longer requires inference. | No further correction required. | No |
| REQ-04 | Minor | `03_functional_requirements.md` FR-09, `09_mvp_definition.md` | Resolved: retrieval fixture must identify expected related source email IDs. | Retrieval influence can be tested. | No further correction required. | No |
| SAF-04 | Major | `03_functional_requirements.md` FR-15/FR-16, `05_domain_model.md`, `07_processing_flow.md` | Resolved: proposal lifecycle states and disallowed execution states are defined. | Calendar safety behavior is implementable. | No further correction required. | No |
| SAF-05 | Major | `03_functional_requirements.md` FR-17, `06_architecture.md`, `07_processing_flow.md` | Resolved: calendar execution must be idempotent per proposal ID. | Retries should not create duplicate events. | No further correction required. | No |
| ARCH-01 | Minor | `06_architecture.md` | Resolved: Calendar Proposal Logic component section added. | FR-15 owner is explicit. | No further correction required. | No |
| ARCH-02 | Minor | `06_architecture.md`, `07_processing_flow.md` | Resolved: sequence diagram routes approval through API/backend. | Backend enforcement is explicit. | No further correction required. | No |
| ARCH-03 | Minor | `07_processing_flow.md` stage 5-6 | Resolved: retrieval must exclude the current email ID. | Self-match retrieval is prevented. | No further correction required. | No |
| DM-01 | Minor | `05_domain_model.md` | Resolved: V1 execution audit trail is defined. | Audit implementation has one canonical path. | No further correction required. | No |
| DM-02 | Minor | `05_domain_model.md` | Resolved: RetrievedContext must preserve source IDs and snippet/source references when used in priority. | Priority reconstruction is preserved. | No further correction required. | No |
| EVAL-01 | Major | `04_nonfunctional_requirements.md`, `09_mvp_definition.md` | Resolved: scenario-based pass/fail plus reported metrics is the MVP evaluation method. | DoD has an objective evaluation style. | No further correction required. | No |

## 11. Proposed Corrections

| Issue ID | Target document | Target section | Text or decision to replace | Proposed replacement | Downstream documents affected |
|---|---|---|---|---|---|
| PATH-01 | Repository structure | Spec source path | `specs/` as canonical path | Resolved: `docs/spec/` is canonical. | All future planning docs |
| SCOPE-01 | `09_mvp_definition.md` | Feature Classification and Definition of Done | Calendar execution as Must | Resolved: calendar execution is Should for MVP. | Tests |
| SCOPE-02 | `03_functional_requirements.md` | FR-18 | `V1 priority: Should` | Resolved: `V1 priority: Must`. | `09_mvp_definition.md`, eval plan |
| TERM-01 | `05_domain_model.md` or new glossary | Separation of Information Types | No canonical glossary entry | Add: "RetrievedContext is the canonical entity for prior-email evidence. Historical context is the source material; RAG is one retrieval method." | FR-09, workflow, UI labels |
| TERM-02 | `03_functional_requirements.md` | FR-03 | Low-value terms not canonicalized | Add subtype enum definition for spam-like, newsletter, automated notification, other low-value. | Domain model, eval fixtures |
| TERM-03 | `05_domain_model.md` | PriorityResult | `deadline_urgency` without urgency definition | Add: "Urgency is a priority factor derived from time sensitivity, not a separate final ranking." | Priority engine tests |
| TERM-04 | `05_domain_model.md` | ProposedAction and CalendarEventProposal | Overlapping action concepts | Add invariant: "CalendarEventProposal is not stored as ProposedAction unless separately shown as a non-side-effect task." | FR-07, FR-15 |
| REQ-01 | `03_functional_requirements.md` | Each FR | No owner field | Add `Owner component` to each FR or maintain a separate owner mapping table. | Architecture, test plan |
| REQ-04 | `09_mvp_definition.md` | Definition of Done | Retrieval influence requirement lacks fixture definition | Add requirement for one labeled pair where expected context source email IDs are known. | Evaluation plan |
| SAF-04 | `05_domain_model.md` | CalendarEventProposal, ToolApproval | Proposal lifecycle incomplete | Define statuses: pending, incomplete, approved, rejected, expired, executing, executed, failed; disallow execution from rejected, expired, executed. | Approval service, UI |
| SAF-05 | `03_functional_requirements.md` | FR-17 | Calendar execution lacks idempotency | Add expected behavior: "Execution must be idempotent per proposal ID and must not create duplicate events on retry." | Calendar tool tests |
| ARCH-01 | `06_architecture.md` | Components | Calendar Proposal Logic only appears in diagram | Add component section with responsibility, inputs, outputs, dependencies, non-responsibilities, failure modes, tests. | FR-15 |
| ARCH-02 | `07_processing_flow.md` | Sequence diagram | Direct UI approval path | Resolved: approval now routes through `UI->>API` then `API->>Approval`, with execution through backend-controlled services. | Safety tests |
| ARCH-03 | `07_processing_flow.md` | Stage 6 | Retrieval does not exclude current email | Add failure-prevention rule: retrieval results must exclude the current email ID. | Retrieval tests |
| DM-01 | `05_domain_model.md` | ToolApproval | Execution audit split unclear | Add invariant: ToolApproval execution fields plus CalendarEventProposal provider fields form the V1 execution audit trail. | Persistence |
| DM-02 | `05_domain_model.md` | RetrievedContext | Context evidence may only be summary | Require `source_email_ids` plus stable snippet text or persisted source reference for any context used in priority factors. | Auditability tests |
| EVAL-01 | New evaluation plan or `09_mvp_definition.md` | Definition of Done | Quantitative evaluation required without targets | Add an evaluation plan defining metrics, fixture fields, and pass thresholds before implementation completion. | Tests, DoD |

## 12. Decisions Requiring User Approval

All decisions from the original review have been answered by the user.

| Question | Why it matters | Options | Recommended option | Consequence of each option |
|---|---|---|---|---|
| Should the canonical spec path be `specs/` or `docs/spec/`? | Future prompts and planning docs need stable paths. | Keep `specs/`; move to `docs/spec/`; duplicate temporarily. | User chose `docs/spec/`. | Applied. |
| Is calendar API execution a Must for V1 or a Should? | FR-17 and MVP disagreed. | Must with sandbox/mock allowed; Should if proposal and approval are enough; V2 if no external write in V1. | User chose Should. | Applied: FR-17 remains Should and MVP no longer requires calendar execution for Definition of Done. |
| Is scoped multilingual handling a Must for V1 or a Should? | FR-18 and MVP disagreed. | Must for two fixture emails; Should if time remains; V2. | User chose Must. | Applied: FR-18 is now Must and MVP requires two non-English fixture emails. |
| What quality targets should the evaluation pipeline use? | DoD requires quantitative evaluation. | Strict numeric thresholds; scenario-based pass/fail for V1; report-only metrics. | User chose scenario pass/fail for MVP. | Applied: NFR-15 and MVP DoD specify scenario-based pass/fail plus reported metrics. |

## 13. Readiness Checklist

- [x] Scope is internally consistent.
- [x] Terminology is canonical for implementation planning.
- [x] All Must requirements are traceable.
- [x] All domain data is representable.
- [x] Every component has a clear boundary.
- [x] Workflows match requirements.
- [x] Safety approval cannot be bypassed by the specified flow.
- [x] Evaluation coverage exists for MVP using scenario-based pass/fail checks plus reported metrics.
- [x] Unresolved decisions are documented in this review.
- [x] MVP remains portfolio-scale.

Step 11 can begin.
