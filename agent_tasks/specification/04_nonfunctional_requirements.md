# Step 4 — Define Non-Functional Requirements

## Prompt

Define the non-functional requirements for the email triage system.

The system is a portfolio-scale AI application, not a production SaaS product, so requirements should be realistic and measurable without unnecessary enterprise complexity.

Cover:

1. Reliability
2. Auditability
3. Safety
4. Privacy
5. Reproducibility
6. Maintainability
7. Performance
8. Testability
9. Observability
10. Configuration management

Important architectural constraints:

- failure to process one email must not crash processing of other emails
- every final priority decision must be explainable through stored contributing factors
- external write actions must require explicit user approval
- credentials and real email contents must never be committed to Git
- LLM outputs used by downstream code must follow structured schemas
- important AI decisions must be evaluable independently of the UI
- the system should be runnable locally using documented setup instructions

For every non-functional requirement provide:

- NFR ID
- Requirement
- Reason
- Verification method

Avoid arbitrary enterprise requirements that provide no value to this project.
