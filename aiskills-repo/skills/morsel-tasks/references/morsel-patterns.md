# Morsel Patterns

## Table of Contents
1. [What is a Morsel?](#what-is-a-morsel)
2. [Morsel Schema](#morsel-schema)
3. [Checkpoint Schema](#checkpoint-schema)
4. [Retry Patterns](#retry-patterns)
5. [Self-Correction Pattern](#self-correction-pattern)
6. [Failure Modes](#failure-modes)

---

## What is a Morsel?

A morsel = the **smallest atomic unit of work** that:
1. Has a single, well-defined action
2. Produces exactly one output (or explicitly nothing)
3. Can be validated before the workflow continues
4. Can be retried independently without side effects

**Not a morsel**: "Build the entire frontend"
**Morsel**: "Write the CSS variables block to `styles/tokens.css`"

---

## Morsel Schema

```json
{
  "id": "m-t1-1",
  "task_ref": "t1",
  "seq": 1,
  "action": "Invoke skill ui-style-generator with prompt='fintech dashboard'",
  "expected_output": "STYLEGUIDE.md with color tokens, typography, and CSS vars",
  "validate": "file STYLEGUIDE.md exists AND has > 50 lines AND contains ':root {'",
  "artifact_type": "markdown",
  "on_fail": "retry",
  "max_retries": 3,
  "self_correct": true,
  "status": "pending | running | done | failed | skipped",
  "attempt": 1,
  "output_artifact": null,
  "error": null,
  "completed_at": null
}
```

### Field Guide

| Field | Description |
|-------|-------------|
| `id` | Unique morsel ID: `m-{task_id}-{seq}` |
| `task_ref` | Parent task ID from task-tree.yaml |
| `action` | Clear imperative description of what to do |
| `expected_output` | What success looks like (used for self-correction) |
| `validate` | How to verify success (file check, schema check, etc.) |
| `on_fail` | `retry` / `skip` / `escalate` |
| `self_correct` | If true, Claude analyzes failure and re-attempts with fix |
| `max_retries` | Max attempts before marking failed (default: 3) |

---

## Checkpoint Schema

Saved to `.workflow/{workflow-id}-checkpoint.json`:

```json
{
  "workflow_id": "wf-mvp-build-001",
  "last_updated": "2026-02-21T10:30:00Z",
  "morsels": {
    "m-t1-1": {
      "status": "done",
      "attempt": 1,
      "output_artifact": "artifacts/001_styleguide.md",
      "completed_at": "2026-02-21T10:25:00Z"
    },
    "m-t1-2": {
      "status": "failed",
      "attempt": 3,
      "error": "API timeout after 30s",
      "completed_at": "2026-02-21T10:28:00Z"
    },
    "m-t2-1": {
      "status": "pending",
      "attempt": 0
    }
  }
}
```

### Lock File Schema

`.workflow/{workflow-id}.lock`:

```json
{
  "workflow_id": "wf-mvp-build-001",
  "pid": 12345,
  "acquired_at": "2026-02-21T10:20:00Z"
}
```

---

## Retry Patterns

### Exponential Backoff

```
Attempt 1 → fail → wait 1s
Attempt 2 → fail → wait 2s
Attempt 3 → fail → wait 4s
→ mark failed, trigger on_fail handler
```

### on_fail Handlers

| Value | Behavior |
|-------|----------|
| `retry` | Retry up to `max_retries` with backoff |
| `skip` | Mark as skipped, continue to next morsel |
| `escalate` | Stop workflow, notify user, await decision |
| `replan` | Signal workflow to trigger Loop-Back Planning |

### When to use each

| Failure type | on_fail |
|-------------|---------|
| API timeout, network error | `retry` |
| Optional enrichment step | `skip` |
| Schema validation failed after retries | `replan` |
| Missing required dependency | `escalate` |
| Non-critical formatting step | `skip` |

---

## Self-Correction Pattern

When `self_correct: true` and output fails validation:

```
morsel exec → output produced → validate output
  ✅ valid → done
  ❌ invalid →
    Claude reads validation error
    Claude reads expected_output description
    Claude identifies fix
    Claude re-executes with corrected approach
    → validate again
    ✅ done
    ❌ → retry with backoff (counts as attempt 2)
```

**Self-correction prompt template** (used internally):
```
The previous attempt produced output that failed validation.

Validation error: {error}
Expected: {expected_output}
Actual output: {actual_output_sample}

Identify what went wrong and re-execute the morsel correctly.
Do not repeat the same mistake.
```

---

## Failure Modes

### Mode 1: Transient failure (retry)
- Network timeout, API rate limit, temporary unavailability
- Response: exponential backoff retry
- After max retries: mark `failed`, trigger `replan`

### Mode 2: Schema validation failure (self-correct)
- Output produced but doesn't match expected contract
- Response: self-correction loop (analyze → fix → retry)
- After 3 self-corrections: mark `failed`, trigger `escalate`

### Mode 3: Dependency missing (escalate)
- Required input artifact from previous task not found
- Response: escalate immediately (don't retry, fix the upstream task first)

### Mode 4: Deterministic failure (skip or escalate)
- Task is fundamentally impossible (wrong skill for the job)
- Response: escalate → workflow triggers Loop-Back Planning

### Loop-Back Planning Trigger

When a morsel is marked `failed` with `on_fail: replan`:
```
morsel_runner exits with code 2
  → workflow skill detects code 2
  → workflow calls task-tree to re-decompose failed task
  → new morsels generated
  → morsel_runner continues with new plan
```
