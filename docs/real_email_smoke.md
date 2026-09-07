# Real Email Smoke Test

This flow is for 3-5 sanitized `.eml` files. It does not read a live mailbox and
does not write to a real calendar.

## Access Needed

- OpenAI API key only.
- No Gmail access.
- No IMAP credentials.
- No calendar credentials.

## Run

Store exported samples under ignored `real-email-smoke/`.

```bash
EMAIL_AGENT_DATABASE_URL=sqlite:///./data/real_email_smoke.db \
EMAIL_AGENT_LLM_PROVIDER=openai \
EMAIL_AGENT_LLM_MODEL=gpt-5 \
EMAIL_AGENT_LLM_API_KEY=... \
EMAIL_AGENT_CALENDAR_PROVIDER=fake \
EMAIL_AGENT_CALENDAR_EXECUTION_ENABLED=false \
uv run uvicorn email_agent.api:create_app --factory --host 127.0.0.1 --port 8000
```

```bash
scripts/real_email_smoke.sh real-email-smoke/message-1.eml
```

Check the inbox UI or API output for summary, action-required, deadlines,
priority, errors, and any proposal status. Calendar proposal execution stays
fake.

## Cleanup

```bash
rm -f data/real_email_smoke.db
```
