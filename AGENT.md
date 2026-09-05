# AGENTS.md

## Authoritative project documents

The following documents define the project:

1. Corrected specifications in `docs/spec/`
2. Accepted ADRs in `docs/decisions/`
3. Technology decisions in `docs/planning/11_technology_decisions.md`
4. Implementation tasks in `docs/planning/12_implementation_roadmap.md`

For every task, read the selected roadmap row and all specifications and ADRs
referenced by that row before making changes.

If these sources conflict, stop and report the conflict instead of choosing
silently.

## Task scope

- Implement exactly one roadmap task per request.
- Do not begin the next task automatically.
- Do not add future functionality or placeholder implementations.
- Do not perform unrelated refactoring or formatting.
- Preserve unrelated user changes.
- Keep the implementation small and human-reviewable.
- Include focused tests in the same task as the implementation.
- If a task is likely to exceed approximately 250–350 meaningful changed lines,
  excluding lockfiles, migrations, fixtures, and generated files, stop and
  propose a smaller split before implementing.

## Preflight

Before modifying files, run:

```bash
git status --short
git branch --show-current
git log -3 --oneline