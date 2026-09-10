# Real LLM Quality Smoke

Use this after `docs/real_email_smoke.md` succeeds with 3-5 sanitized `.eml`
files. Do not paste or commit raw private email text.

## Checklist

For each processed message, record only aggregate notes:

- Summary is faithful and does not invent sender intent.
- Category is reasonable.
- `action_required` matches the actual request.
- Deadlines and meetings are present only when supported by the message.
- Priority explanation is grounded in stored factors.
- Errors are per-email and do not stop the batch.
- Logs include model, latency, retry count, and token counts when returned.

## Report

Copy `docs/templates/real_llm_smoke_report.md` outside the repo or fill it with
non-sensitive aggregate notes only.
