# Non-Functional Requirements

## NFR-01 Reliability

- Requirement: Failure to process one email must not stop processing of other emails.
- Reason: A single malformed message should not make the whole triage run unusable.
- Verification method: Run a fixture inbox containing one malformed email and verify the batch completes with per-email error status.

## NFR-02 Auditability

- Requirement: Every final priority decision must store contributing factors, source signal identifiers, retrieved context used, and user preferences applied.
- Reason: The user must be able to understand and debug why an email was ranked.
- Verification method: Inspect persisted priority results and confirm each has reconstructable factors without re-running the LLM.

## NFR-03 Safety

- Requirement: External write actions must require explicit user approval and must be isolated behind a calendar tool service.
- Reason: The system should not make side effects based only on model inference.
- Verification method: Automated tests verify calendar writes fail or are blocked without approved ToolApproval records and that unauthorized external writes remain at zero.

## NFR-04 Privacy

- Requirement: Credentials, API tokens, and real email contents must never be committed to Git.
- Reason: Email data is sensitive and the project may be published as a portfolio artifact.
- Verification method: Use `.gitignore`, example env files, synthetic fixtures, and secret scanning before publication.

## NFR-05 Reproducibility

- Requirement: The project must include deterministic fixtures and documented commands for setup, processing, tests, and evaluation.
- Reason: Another developer should be able to reproduce the demo locally.
- Verification method: Run setup from a clean checkout using documented instructions and verify expected outputs.

## NFR-06 Structured AI Output

- Requirement: LLM outputs used by downstream code must conform to explicit schemas and be validated before persistence or priority calculation.
- Reason: Unvalidated free-form model output can break deterministic processing.
- Verification method: Unit tests feed valid and invalid model outputs into schema validation.

## NFR-07 Maintainability

- Requirement: Core responsibilities must remain separated across ingestion, preprocessing, retrieval, LLM analysis, priority calculation, persistence, approval, calendar tooling, and UI.
- Reason: Clear boundaries make the portfolio project easier to reason about and extend.
- Verification method: Architecture review confirms each component can be tested independently and avoids circular responsibility.

## NFR-08 Performance

- Requirement: A local V1 demo should process a small representative inbox, such as 25 to 100 emails, within a practical interactive workflow.
- Reason: Portfolio evaluation should not require production-scale infrastructure.
- Verification method: Measure processing time on fixture data and document expected runtime.

## NFR-09 Testability

- Requirement: Important AI decisions must be evaluable independently of the UI.
- Reason: Model behavior, extraction quality, and priority logic need objective checks.
- Verification method: Provide tests or eval scripts for schema conformance, extraction examples, priority factors, retrieval influence, and approval gating.

## NFR-10 Observability

- Requirement: Processing should produce structured logs or status records for each major stage and failure.
- Reason: Users and developers need visibility into why a message failed or why processing took a path.
- Verification method: Process a fixture inbox and verify stage status is available for each email.

## NFR-11 Configuration Management

- Requirement: Runtime configuration must be documented and separated from code, with safe example files for required variables.
- Reason: The app needs local configuration without committing secrets.
- Verification method: Confirm the app starts with documented local config and fails clearly when required settings are absent.

## NFR-12 Local Runnable Scope

- Requirement: V1 should be runnable locally without requiring production authentication, deployment infrastructure, or continuous background workers.
- Reason: The intended artifact is a small demonstrable portfolio project.
- Verification method: Follow local setup instructions and run ingestion, analysis, UI, tests, and evaluation locally.

## NFR-13 Multilingual Evaluation

- Requirement: The fixture and evaluation set should include at least two non-English emails in explicitly listed supported languages, including one action-oriented email and one date or meeting example.
- Reason: Multilingual behavior should be demonstrated with measurable examples rather than assumed from model capability.
- Verification method: Run the evaluation pipeline and verify schema conformance, summary/explanation output language, action detection, and date or meeting extraction on the non-English fixtures.

## NFR-14 Locale-Aware Date Handling

- Requirement: Date and time extraction should record locale assumptions, timezone assumptions, and uncertainty when a non-English or locale-specific expression cannot be normalized confidently.
- Reason: Date formats and natural-language references can be ambiguous across languages and regions.
- Verification method: Test fixture emails with locale-specific date formats and verify normalized values or explicit uncertainty fields are produced.

## NFR-15 MVP Evaluation Method

- Requirement: MVP evaluation should use scenario-based pass/fail checks plus reported metrics rather than strict numeric model-quality thresholds.
- Reason: The project needs objective V1 acceptance without pretending a small portfolio fixture set can support statistically meaningful model benchmarks.
- Verification method: Run the evaluation pipeline and confirm each required scenario reports pass/fail status, supporting evidence, and any available metric values.
