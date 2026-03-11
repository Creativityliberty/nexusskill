---
name: orchestra-forge
description: Full-stack AI agent builder that combines Nüm Agents architecture (YAML spec + universes), PocketFlow execution engine (nodes/flows/async), and Skill Architect quality pipeline. Use when the user wants to design, build, and validate a complete AI agent from scratch in one guided workflow. Triggers on "orchestra-forge", "/orchestra-forge", "build a complete agent", "generate a full agent", "create an agent with pocketflow and num-agents", "forge an agent", "design and build an agent".
---

# Orchestra Forge — Full-Stack Agent Builder

Guides you through the **complete lifecycle** of building an AI agent:
from high-level architecture (Nüm Agents YAML spec) → execution engine (PocketFlow) → quality audit (Skill Architect pipeline).

Each phase is independent. You can stop at any phase (just the spec, just the code, or the full pipeline).

---

## Phase 1 — ARCHITECT (Nüm Agents Spec)

**Goal**: Translate user intent into a structured `agent.yaml`.

### 1.1 — Gather Requirements

Ask the user:

- What does the agent **do**? (task in one sentence)
- What are the **inputs** and **outputs**?
- Does it need **memory** (past interactions), **scheduling**, or **event-driven** triggers?
- What **LLM** backend? (default: `claude-sonnet-4-5`, or `gpt-4o`)
- Single agent or **multi-agent** system?

### 1.2 — Recommend Universes

Based on the answers, select universes from the catalog:

| Need | Universe |
|------|----------|
| Any multi-step flow | `PocketFlowCore` (always include) |
| Structured LLM output | `StructureAgentIA` |
| Decision branching | `ConditionalFlow` |
| Memory / conversations | `KnowledgeLayer` + `memory: true` |
| Document Q&A | `RAGUnivers` |
| Agent-to-agent comms | `EventBusUnivers` |
| External APIs | `APIConnectorUnivers` |
| Production monitoring | `MetricsUnivers` + `TracingUnivers` |

See full catalog: [../num-agents/references/universe-catalog.md](../num-agents/references/universe-catalog.md)

### 1.3 — Generate `agent.yaml`

```yaml
agent:
  name: "<AgentName>"
  description: "<What it does>"
  univers:
    - PocketFlowCore
    - StructureAgentIA
    # add more as needed
  protocol: N2A
  llm: claude-sonnet-4-5
  memory: false
  eventbus: false
  scheduler: false
  metrics: false
  tracing: false

flows:
  - name: main
    nodes:
      - <Node1>
      - <Node2>
    transitions:
      - from: <Node1>
        to: <Node2>
        on: default
```

Full YAML schema: [../num-agents/references/agent-spec-schema.md](../num-agents/references/agent-spec-schema.md)
Flow patterns: [../num-agents/references/flow-patterns.md](../num-agents/references/flow-patterns.md)

**Checkpoint ✅** — Show `agent.yaml` to user. Ask: "Does this spec match your intent? Want to adjust any universe or flow?"

---

## Phase 2 — SCAFFOLD (PocketFlow Implementation)

**Goal**: Turn the YAML spec into working Python code using PocketFlow.

### 2.1 — Copy the PocketFlow Engine

```bash
cp path/to/skills/pocketflow/scripts/pocketflow.py ./pocketflow.py
```

The library is at: [../pocketflow/scripts/pocketflow.py](../pocketflow/scripts/pocketflow.py)

### 2.2 — Map Nodes

For each node declared in `agent.yaml`, implement a PocketFlow `Node`:

```python
from pocketflow import Node, Flow

class <NodeName>(Node):
    def prep(self, shared):
        # Read inputs from shared store
        return shared["<input_key>"]

    def exec(self, prep_res):
        # Core logic: LLM call, API, transform
        return call_llm(f"<prompt> {prep_res}")

    def post(self, shared, prep_res, exec_res):
        shared["<output_key>"] = exec_res
        return "default"  # or "retry", "done", custom action
```

### 2.3 — Add Hooks (if KnowledgeLayer or MetricsUnivers included)

```python
import time

node.add_before_hook(lambda shared: shared.update({"start_time": time.time()}))
node.add_after_hook(lambda shared, result:
    shared.update({"duration": time.time() - shared["start_time"]}))
node.add_error_hook(lambda shared, err:
    print(f"[ERROR] {err}"))
```

### 2.4 — Wire the Flow

```python
# Linear
node_a >> node_b >> node_c

# Conditional
node_a - "retry" >> node_a   # loop back
node_a - "done" >> node_b    # proceed

flow = Flow(start=node_a)
```

### 2.5 — Add Async (if parallel or async processing needed)

```python
from pocketflow import AsyncNode, AsyncParallelBatchNode, AsyncFlow

class MyAsyncNode(AsyncNode):
    async def exec_async(self, prep_res):
        return await async_llm_call(prep_res)
```

### 2.6 — Run and Test

```python
shared = {"input": "<user request>"}
flow.run(shared)
print(shared["<output_key>"])
```

**Checkpoint ✅** — Show full `agent.py`. Ask: "Shall I add retries, async, batch processing, or run a test?"

---

## Phase 3 — FORGE (Skill Architect Quality Pass)

**Goal**: Run a 5-role audit on the generated agent code and spec.

Run each role in sequence. Produce structured output per role:

### Role 1 — Architecture Analyst

Review `agent.yaml` and `agent.py`:

- Are all declared universes actually used in the code?
- Is the flow graph complete (no orphan nodes)?
- Are transitions exhaustive (every `post()` return value has a target)?

### Role 2 — Code Refactorer

- Add error handling to all `exec()` methods
- Replace hardcoded prompts/values with parameters
- Ensure `SharedStore` keys are consistent (no typos between nodes)
- Add `max_retries` on LLM-calling nodes

### Role 3 — Skill Reviewer

- Does the flow implement exactly what `agent.yaml` declares?
- Are async nodes used where they should be (parallel tasks)?
- Is `SharedStore` minimal (no unused keys)?

### Role 4 — Security Auditor

- No secrets or API keys hardcoded
- User inputs are sanitized before being embedded in prompts (prompt injection risk)
- File paths from user input are validated
- Network calls have timeouts

### Role 5 — Documentation Enhancer

- Add docstrings to all Node classes
- Add inline comments for non-obvious logic
- Generate a `README.md` for the agent with usage example

**Final summary table:**

```
## ✅ Orchestra Forge — Complete

| Phase | Status | Output |
|-------|--------|--------|
| Architect | ✅ | agent.yaml |
| Scaffold | ✅ | agent.py + pocketflow.py |
| Forge Audit | ✅ | Refactored code + docs |
```

---

## Output Checklist

- [ ] `agent.yaml` — Nüm Agents spec with universes declared
- [ ] `pocketflow.py` — execution engine (copied from skill)
- [ ] `agent.py` — PocketFlow nodes + flow wiring
- [ ] `agent.py` — hooks, retries, error handling added
- [ ] Forge audit passed (5 roles)

---

## References

- Universe catalog: [../num-agents/references/universe-catalog.md](../num-agents/references/universe-catalog.md)
- YAML schema: [../num-agents/references/agent-spec-schema.md](../num-agents/references/agent-spec-schema.md)
- Flow patterns: [../num-agents/references/flow-patterns.md](../num-agents/references/flow-patterns.md)
- PocketFlow engine: [../pocketflow/scripts/pocketflow.py](../pocketflow/scripts/pocketflow.py)
- Skill Architect roles: [../skill-architect/references/agent-roles.md](../skill-architect/references/agent-roles.md)
