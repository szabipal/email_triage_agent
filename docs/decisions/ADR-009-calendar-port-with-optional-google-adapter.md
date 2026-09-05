# ADR-009: Calendar Port With Optional Google Adapter

## Status
Accepted

## Context
Calendar proposals and approval gating are Must for V1. Calendar execution is Should. External writes must be isolated, approval-gated, replaceable, idempotent, and testable without a real provider. This supports FR-15, FR-16, FR-17, NFR-03, NFR-04, and the safety audit.

## Decision
Use a calendar interface/port with a fake adapter for tests and development. Use Google Calendar as the intended real demonstration adapter if calendar execution is implemented.

## Alternatives considered
Direct Google Calendar calls, Microsoft Graph Calendar, CalDAV, and no real provider.

## Consequences
Approval enforcement lives in backend/application services before adapter execution. Tests can assert zero unauthorized writes with the fake adapter. Google Calendar offers recognizable demo value. The trade-off is OAuth/API setup if the real adapter is used.

## Reversal strategy
Implement another adapter behind the same calendar port. Preserve proposal IDs and idempotency keys so execution audit behavior remains stable.
