---
name: morsel-tasks
description: Execute tasks as atomic "morsels" — the smallest indivisible unit of work. Handles checkpointing (resume where interrupted), lock files (prevent concurrent runs), exponential backoff retry, and self-correction when output doesn't match expected schema. Used as Phase 2 of the workflow system. Triggers on "execute morsels", "run task atomically", "resume interrupted workflow", "/morsel-tasks".
---

# Morsel Tasks

A morsel is the smallest indivisible unit of work in a workflow.
This skill executes morsels one by one with: checkpoint/resume, lock files, retry with backoff, and schema validation before marking `done`.

## Core Concepts

```
Morsel  = one atomic action → one validated output
Checkpoint = saved state in .workflow/checkpoint.json (resume on interrupt)
Lock    = .workflow/lock (prevent concurrent runs)
Backoff = retry 1s → 2s → 4s (exponential)
Self-Correction = if output fails schema → Claude fixes it before next morsel
```

## Morsel States

```
pending → running → done
                 ↘ failed → retry → running
                          ↘ (max retries) → skipped | escalate
```

## Workflow

### 1. Load Task Tree

Read `task-tree.yaml` (or `.workflow/task-tree.yaml`). Pick the first unblocked task.

### 2. Acquire Lock

```bash
python skills/morsel-tasks/scripts/morsel_runner.py lock --workflow-id <id>
```

Fails if lock exists (another process is running). Releases on completion or crash.

### 3. Load/Init Checkpoint

```bash
python skills/morsel-tasks/scripts/morsel_runner.py status --workflow-id <id>
```

If checkpoint exists → skip already-completed morsels and resume from last `done`.

### 4. Execute Each Morsel

For each morsel in the current task:

```
[m1] Action: invoke skill 'ui-style-generator' with prompt=...
     → Execute
     → Validate output against schema (see artifacts-maker references/artifact-types.md)
     ✅ done → checkpoint updated → register artifact
     ❌ fail → wait 1s → retry (max 3) → mark failed or escalate
```

**Self-Correction loop** (Schema-First):
```
exec morsel → get output → validate schema
  if invalid → Claude analyzes error → re-executes with fix → validate again
  if still invalid after 3 attempts → mark morsel as 'failed', escalate
```

### 5. Run the Morsel Runner

```bash
# Execute all pending morsels for a task
python skills/morsel-tasks/scripts/morsel_runner.py run \
  --workflow-id my-workflow \
  --task-id t1 \
  --tree task-tree.yaml

# Resume after interruption (reads checkpoint automatically)
python skills/morsel-tasks/scripts/morsel_runner.py run \
  --workflow-id my-workflow --resume

# Show current status
python skills/morsel-tasks/scripts/morsel_runner.py status --workflow-id my-workflow
```

### 6. Register Artifact on Completion

After each morsel → call `artifacts-maker`:

```bash
python skills/artifacts-maker/scripts/artifact_registry.py add \
  --file <output-file> --type <artifact-type> \
  --task-id <task-id> --skill <skill-name>
```

### 7. Release Lock

```bash
python skills/morsel-tasks/scripts/morsel_runner.py unlock --workflow-id <id>
```

Called automatically by `morsel_runner.py run` on completion/error.

## Checkpoint File Format

See [references/morsel-patterns.md](references/morsel-patterns.md) for checkpoint schema and retry patterns.

## Wrap Up

- ✅ Task `<id>` complete: `N` morsels executed
- Show morsel table: id | action | status | attempts | artifact
- Artifacts registered: `N`
- Ask: "Continue to next task or run `workflow` to proceed automatically?"
