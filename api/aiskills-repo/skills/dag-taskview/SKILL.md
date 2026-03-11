---
name: dag-taskview
description: Visual DAG (Directed Acyclic Graph) task tree system for project decomposition and tracking. Generates Mermaid diagrams showing task dependencies, progress, critical paths, and blockers. Use when user says "show task tree", "create a DAG", "task dependencies", "visualize my tasks", "project progress", "critical path", "/dag", "/tasks". Works standalone or chains from blueprint-maker.
---

# DAG TaskView — Visual Task Tree System

Decomposes complex projects into **visual DAG-based task trees** with dependency tracking, progress monitoring, and critical path analysis.

## When to use

- User wants to **visualize** tasks and their dependencies
- User needs to see **what's blocking** progress
- User wants to know the **critical path** (longest dependency chain)
- After running `blueprint-maker`, to convert phases into visual tasks

## Step 1: Define Tasks

Accept tasks from the user in any format:

- Natural language: "Build auth, then API endpoints, then tests"
- YAML file (see templates/task_template.yaml)
- From blueprint-maker output

### Task format

```yaml
project: "Project Name"
tasks:
  - id: unique_id
    name: "Human readable name"
    status: pending  # pending | in_progress | done | blocked
    deps: []         # list of task IDs this depends on
```

## Step 2: Build the DAG

Run the engine:

```python
python scripts/dag_engine.py --input tasks.yaml --output dag.md
```

The engine:

1. Parses tasks and dependencies
2. Validates the DAG (detects cycles)
3. Computes the critical path
4. Renders a Mermaid diagram

## Step 3: Render Visualization

The output is a Mermaid diagram with color-coded status:

```
✅ Done       → Green  (#22c55e)
🔄 In Progress → Yellow (#eab308)
⏳ Pending    → Gray   (#64748b)
🚫 Blocked    → Red    (#ef4444)
```

## Step 4: Track Progress

Update task statuses and regenerate the diagram:

```python
from scripts.progress_tracker import ProgressTracker

tracker = ProgressTracker("tasks.yaml")
tracker.update("auth", "done")
tracker.update("api", "in_progress")
tracker.render("progress.md")
tracker.summary()  # Shows % complete, blockers, critical path
```

## Step 5: Analyze

The engine provides:

- **Progress %**: How much is done
- **Critical Path**: The longest chain (determines minimum project time)
- **Blockers**: Tasks that are blocked and what's blocking them
- **Next Actions**: Tasks that can start now (all deps satisfied)

## Integration

| Skill | Integration |
|---|---|
| `blueprint-maker` | `engine.to_dag_tasks(blueprint)` → feed into DAG |
| `flow-orchestrator` | Map DAG tasks to PocketFlow nodes for execution |
| `orchestra-forge` | Use DAG to validate flow completeness |

## Examples

- "Show me the task tree for building a REST API" → Auto-decompose + visualize
- "Here are my tasks in YAML, create a DAG" → Parse + render
- "What's the critical path for this project?" → Analyze + highlight
- "Mark authentication as done, update the diagram" → Track + refresh
