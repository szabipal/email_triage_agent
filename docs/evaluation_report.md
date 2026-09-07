# Evaluation Report

Generated from `proposed/config/eval.dev.json` against
`datasets/fixtures/dev.jsonl`.

## Dataset

- Split: `dev`
- Records: 8 synthetic emails
- Scenarios: action, calendar proposal, context-dependent, context-source,
  deadline, fallback, low-value, malformed, meeting, multilingual, newsletter,
  priority, and thread
- Prediction source: fixture-label fake provider

## Variants

| Variant | Purpose |
| --- | --- |
| `llm_only` | Analysis and priority without retrieval or preferences |
| `llm_rag` | Adds retrieval context |
| `full_system` | Adds retrieval plus preference behavior |

## Results

All full-system scenarios passed. No unauthorized calendar writes were recorded.

| Area | Full system result |
| --- | --- |
| Classification | 1.0 category, low-value, and action accuracy |
| Extraction | 1.0 action, deadline, and meeting count accuracy |
| Summary | 1.0 faithfulness pass rate |
| Retrieval | 1.0 recall at 3 over 1 evaluated record |
| Priority | 1.0 band accuracy |
| Preferences | 1.0 adherence pass rate |
| Calendar | 1.0 proposal pass rate |

## Limits

The report is deterministic and fixture-backed. It proves the local workflow,
schema contracts, retrieval labels, preference path, and approval gate, but it
does not claim production LLM quality or real mailbox coverage.
