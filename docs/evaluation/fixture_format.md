# Evaluation Fixture Format

Synthetic inbox records are newline-delimited JSON. Each line validates as
`email_agent.evaluation.FixtureRecord`.

Required top-level fields:

- `id`: stable fixture row ID.
- `split`: `dev` or `test`.
- `scenario_ids`: one or more scenario tags.
- `email`: an `email_agent.domain.Email` payload.
- `labels`: expected analysis and retrieval labels.

Label fields cover category, action-required status, low-value type, priority
band, optional action/deadline/meeting candidates, multilingual support, and
expected related source email IDs for retrieval checks.
