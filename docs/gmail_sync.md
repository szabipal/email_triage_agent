# Gmail Sync

Gmail sync is local-first. It imports recent unread messages, processes them
through the existing triage pipeline, and can optionally write AI labels back to
Gmail. Calendar execution remains disabled unless you separately configure it.

## Google Setup

1. Create a Google Cloud project.
2. Enable the Gmail API.
3. Configure an OAuth consent screen for local testing.
4. Create an OAuth client of type **Desktop app**.
5. Download the client JSON file.
6. Store it outside Git, for example:

```text
secrets/google_oauth_client.json
```

The `secrets/` directory is not committed if you keep it untracked; do not put
OAuth client files or tokens in Git.

## Environment

Set these values in `.env`:

```text
EMAIL_AGENT_LLM_PROVIDER=openai
EMAIL_AGENT_LLM_MODEL=gpt-5.6-luna
EMAIL_AGENT_LLM_API_KEY=...
EMAIL_AGENT_LLM_MAX_BODY_CHARS=8000

EMAIL_AGENT_GMAIL_CREDENTIALS_PATH=./secrets/google_oauth_client.json
EMAIL_AGENT_GMAIL_TOKEN_PATH=./data/gmail_token.json
EMAIL_AGENT_GMAIL_SYNC_QUERY=label:UNREAD
EMAIL_AGENT_GMAIL_SYNC_LIMIT=10
EMAIL_AGENT_GMAIL_LABEL_WRITE_ENABLED=false

EMAIL_AGENT_CALENDAR_PROVIDER=fake
EMAIL_AGENT_CALENDAR_EXECUTION_ENABLED=false
```

On first sync, the backend starts a local OAuth browser flow and stores the
refresh token at `EMAIL_AGENT_GMAIL_TOKEN_PATH`.

Leave `EMAIL_AGENT_GMAIL_LABEL_WRITE_ENABLED=false` for read-only sync. Set it
to `true` only when you want the app to create and apply Gmail labels such as
`AI/Billing`, `AI/Security`, and `AI/Action Required`.

When enabling label writes after a read-only authorization, delete the old token
and approve the broader Gmail permission again:

```bash
rm -f data/gmail_token.json
```

The app applies these labels when analysis succeeds:

```text
AI/Action Required
AI/Billing
AI/Calendar
AI/Jobs
AI/Meeting
AI/Newsletter
AI/Promotion
AI/Security
AI/Work
AI/Other
```

Category labels come from the LLM's `category` field. `AI/Action Required` is
added when `action_required=true`, and `AI/Calendar` is added when the analysis
creates deadline or meeting proposals.

## Run

Start the API:

```bash
uv run uvicorn email_agent.api:create_app --factory --host 127.0.0.1 --port 8000
```

Start the UI:

```bash
npm --prefix frontend run dev
```

Open `http://127.0.0.1:5173` and click **Sync Gmail**.

By default, sync imports up to 10 unread messages matching `label:UNREAD`.
Imported messages are deduplicated by Gmail message ID. When label writing is
enabled, successful analyses also apply category labels in Gmail.

## Cost Control

The LLM receives the cleaned/normalized subject and body, not the raw MIME
message. `EMAIL_AGENT_LLM_MAX_BODY_CHARS` caps the cleaned body sent to the LLM;
the default is 8000 characters.
