# ADR-013: Pytest With Deterministic Fakes

## Status
Accepted

## Context
The system requires unit, integration, API, database, retrieval, LLM contract, calendar approval, end-to-end, and evaluation tests. Tests must run without paid external services. This supports NFR-01, NFR-03, NFR-05, NFR-06, NFR-09, NFR-13, NFR-15, and the MVP Definition of Done.

## Decision
Use pytest as the primary test runner with deterministic fakes for LLM, embedding, calendar, email source, and clock dependencies. Use pytest-asyncio where async behavior needs direct testing.

## Alternatives considered
unittest, behave/Cucumber-style tests, live-provider integration tests as defaults, and Playwright-only end-to-end testing.

## Consequences
Tests remain fast and deterministic. Provider behavior can be simulated for error cases and approval bypass checks. The trade-off is maintaining realistic fake adapters and fixtures.

## Reversal strategy
Keep test fixtures and provider ports stable. Add live-provider smoke tests separately without replacing the deterministic test suite.
