---
name: flow-orchestrator
description: Advanced multi-agent workflow orchestration engine built on PocketFlow. Use when building complex multi-agent pipelines that need pause/resume, state snapshots, execution tracing, and coordinated agent pools. Combines orchestra-forge, kernel-forge, and pocketflow into a unified runtime.
---

# Flow Orchestrator

A production-grade multi-agent orchestration skill that extends PocketFlow with runtime control, observability, and resilience.

## When to use this skill

- Building **complex multi-agent pipelines** (e.g., Planner → Workers → Reviewer)
- Need **pause/resume** for long-running LLM workflows
- Need **state snapshots** for rollback and debugging
- Need **execution tracing** with timestamps, diffs, and transition logs
- Coordinating **parallel agents** with message queues

## Core Components

### 1. `OrchestratorRuntime` (scripts/orchestrator.py)

Wraps PocketFlow Flows with runtime control:

- `runtime.run(shared)` — Start the pipeline
- `runtime.pause()` — Freeze execution between nodes
- `runtime.resume()` — Continue from last pause point
- `runtime.status()` — Get current node, elapsed time, state

### 2. `Tracer` (scripts/tracer.py)

Logs every node transition:

- Entry/exit timestamps per node
- Shared data diffs (what changed)
- Action edges taken
- Retry/fallback events
- Export to JSON or Mermaid diagram

### 3. `SnapshotManager` (scripts/snapshot.py)

State persistence:

- `save(shared, label)` — Serialize shared data to disk
- `load(label)` — Restore from a checkpoint
- `list()` — Show all available snapshots
- `diff(a, b)` — Compare two snapshots

### 4. `AgentPool` (scripts/orchestrator.py)

Multi-agent coordination via asyncio queues:

- Spawn N worker agents
- Round-robin or priority-based task dispatch
- Collect and merge results

## How to use it

### Step 1: Define your agents as PocketFlow Nodes

```python
from pocketflow import Node, Flow, AsyncNode, AsyncFlow

class PlannerAgent(Node):
    def prep(self, shared):
        return shared["task_description"]
    
    def exec(self, task):
        return call_llm(f"Break this into subtasks:\n{task}")
    
    def post(self, shared, prep_res, exec_res):
        shared["subtasks"] = parse_subtasks(exec_res)
        return "dispatch"
```

### Step 2: Wire the flow

```python
planner = PlannerAgent()
workers = WorkerPool()  # BatchNode for parallel execution
reviewer = ReviewerAgent()
finalizer = FinalizeNode()

planner - "dispatch" >> workers
workers - "review" >> reviewer
reviewer - "approved" >> finalizer
reviewer - "retry" >> planner

pipeline = Flow(start=planner)
```

### Step 3: Run with the Orchestrator

```python
from scripts.orchestrator import OrchestratorRuntime

runtime = OrchestratorRuntime(pipeline, enable_trace=True, enable_snapshots=True)
shared = {"task_description": "Build a REST API for user management"}

# Run (can be paused mid-execution)
runtime.run(shared)

# After completion:
runtime.tracer.export("trace.json")
runtime.tracer.to_mermaid("trace.md")
```

### Step 4: Pause and Resume

```python
# In another thread or signal handler:
runtime.pause()  # Freezes after current node completes

# Later:
runtime.resume()  # Picks up where it left off
```

### Step 5: Snapshots

```python
from scripts.snapshot import SnapshotManager

sm = SnapshotManager(directory=".snapshots")
sm.save(shared, label="after-planning")

# ... something goes wrong ...
shared = sm.load("after-planning")  # Rollback!
```

## Decision Tree

```
Is your task a single LLM call?
├── YES → Use a simple Node, not this skill
└── NO → Is it a linear pipeline?
    ├── YES → Use pocketflow Workflow pattern
    └── NO → Does it need multiple agents?
        ├── YES → Use this skill (flow-orchestrator)
        └── NO → Does it need pause/resume or tracing?
            ├── YES → Use this skill
            └── NO → Use orchestra-forge
```

## Integration with other skills

- **pocketflow**: This skill extends PocketFlow. All Node/Flow/Batch/Async primitives work.
- **orchestra-forge**: Use orchestra-forge templates as sub-flows inside the orchestrator.
- **kernel-forge**: The orchestrator can delegate to kernel-forge for policy enforcement and idempotency.
- **skill-architect**: Run skill-architect to audit your orchestrated pipelines.
