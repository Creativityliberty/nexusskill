---
name: num-agents
description: Build, scaffold, and design AI agent systems using the Nüm Agents SDK — a universe-based orchestration framework. Use when the user wants to create an agent from a YAML spec, design a multi-agent flow, add execution hooks, build conditional branching, wire universes together, or scaffold a new Nüm Agents project. Triggers on "create a num-agents agent", "scaffold an agent", "build an agent with universes", "num-agents", "/num-agents", "generate agent spec".
---

# Nüm Agents SDK Skill

Scaffold, design, and build AI agent systems using the Nüm Agents SDK.
The SDK uses a **universe-based architecture**: declare which functional modules
your agent needs, and the framework generates the scaffolding automatically.

Install: `pip install num-agents`
Repo: https://github.com/Creativityliberty/numagents

## Core Concepts

```
Universe   ← functional module (PocketFlowCore, KnowledgeLayer, etc.)
Node       ← single execution step with retry + hooks
Flow       ← graph of nodes with conditional transitions
SharedStore← dict passed through all nodes (global state)
Agent Spec ← YAML declaration → auto-generates agent code
```

See [references/universe-catalog.md](references/universe-catalog.md) for all available universes.
See [references/flow-patterns.md](references/flow-patterns.md) for Node, Flow, ConditionalNode patterns.
See [references/agent-spec-schema.md](references/agent-spec-schema.md) for the YAML spec schema.

## Workflow

### 1. Understand the Agent

Ask the user:
- What does the agent need to **do**? (e.g. summarize docs, call APIs, orchestrate sub-agents)
- Which **universes** does it need? (see universe-catalog.md)
- Does it need **memory**, **event bus**, **scheduler**, **metrics**, **tracing**?
- What **LLM** backend? (gpt-4o, claude-sonnet-4-6, etc.)

### 2. Write the Agent Spec (YAML)

Generate `agent.yaml` following the schema in [references/agent-spec-schema.md](references/agent-spec-schema.md):

```yaml
agent:
  name: "MyAgent"
  description: "What this agent does"
  univers:
    - PocketFlowCore       # node/flow execution engine
    - StructureAgentIA     # structured output + reasoning
    - KnowledgeLayer       # memory and retrieval
  protocol: N2A
  llm: claude-sonnet-4-6
  memory: true
  eventbus: false
  scheduler: false
  metrics: true
  tracing: true
```

### 3. Generate the Scaffold

```bash
num-agents generate --spec agent.yaml --catalog univers_catalog.yaml
```

If no catalog exists yet:
```bash
num-agents generate --spec agent.yaml  # uses default catalog
```

### 4. Implement Nodes

For each step in the agent's workflow, implement a Node:

```python
from num_agents import Node, SharedStore

class MyNode(Node):
    def __init__(self):
        super().__init__(
            name="MyStep",
            retry_count=3,
            enable_logging=True
        )

    def exec(self, shared: SharedStore):
        data = shared.get("input_key")
        result = process(data)
        shared.set("output_key", result)
        return result
```

For conditional branching: see [references/flow-patterns.md](references/flow-patterns.md#conditional-nodes).

### 5. Wire the Flow

```python
from num_agents import Flow

flow = Flow(name="MyPipeline", enable_logging=True)
flow.add_node(node_a)
flow.add_node(node_b)
flow.set_start(node_a)
node_a.connect(node_b)  # linear connection
```

### 6. Add Hooks

```python
import time

node.add_before_hook(lambda shared: shared.set("start_time", time.time()))
node.add_after_hook(lambda shared, result:
    shared.set("duration", time.time() - shared.get("start_time")))
node.add_error_hook(lambda shared, error:
    logger.error(f"Node failed: {error}"))
```

### 7. Run the Agent

```python
results = flow.execute(initial_data={
    "config": {...},
    "input": "user request here"
})
print(results)
```

### 8. Dev Setup (new project)

```bash
git clone https://github.com/Creativityliberty/numagents.git
cd numagents
make install-dev   # installs deps + pre-commit hooks
make check         # lint + type-check + tests
make test-cov      # coverage report
```

## Wrap Up

- ✅ Agent spec: `agent.yaml` created
- ✅ Nodes implemented: [list]
- ✅ Flow wired: [node_a → node_b → ...]
- ✅ Hooks added: [before/after/error]
- Ask: "Do you want me to add metrics/tracing, a ConditionalNode, or run `make check`?"
