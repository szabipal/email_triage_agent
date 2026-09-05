# ADR-006: Replaceable LLM Provider Port

## Status
Accepted

## Context
The system requires structured LLM analysis, schema validation, retries, malformed-output handling, timeouts, provider configuration, fake model tests, and prompt version tracking without coupling domain logic to one provider. This supports FR-03 through FR-08, FR-12, FR-18, NFR-06, NFR-09, and the AI responsibility specification.

## Decision
Use a plain Python LLM provider port with real and fake adapters. Do not use an agent framework for V1.

## Alternatives considered
Direct provider SDK calls throughout services, LangChain, LlamaIndex agents, and a general agent framework.

## Consequences
Domain logic remains provider-agnostic and testable. Structured responses are validated before use. Fake adapters make deterministic tests possible. The trade-off is writing a small amount of application-owned adapter code.

## Reversal strategy
Add a new adapter implementing the same port for another provider or framework. Keep prompts, schemas, and service contracts stable.
