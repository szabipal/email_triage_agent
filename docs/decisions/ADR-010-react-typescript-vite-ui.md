# ADR-010: React TypeScript Vite UI

## Status
Accepted

## Context
The project requires a simple usable UI and should demonstrate backend/API engineering. The UI must show prioritized inbox data, details, explanations, retrieved context, proposals, approval/rejection, and status without calculating authoritative priority. This supports FR-14, FR-16, NFR-07, NFR-10, and the MVP UI requirements.

## Decision
Use a small React/TypeScript frontend built with Vite.

## Alternatives considered
Streamlit and server-rendered HTML.

## Consequences
React demonstrates a clean API boundary and gives enough UI flexibility for inbox/detail workflows. TypeScript improves frontend contract discipline. The trade-off is more setup and testing effort than Streamlit.

## Reversal strategy
Keep the backend API authoritative and stable. Replace the frontend with Streamlit or server-rendered views if timeline pressure outweighs frontend portfolio value.
