---
name: kernel-forge
description: Build a complete WMAG Kernel (World Model + Action Graph) — a production-grade multi-agent orchestration system with multi-tenant Action Registry, LLM Planner, Policy Gate, idempotent execution, and SSE streaming. Based on the Os-frame architecture. Use when the user wants to build a production AI OS, an orchestration kernel, a multi-tenant agent system, a WMAG kernel, or needs policy-gated deterministic agent execution. Triggers on "kernel-forge", "/kernel-forge", "build a WMAG kernel", "build a multi-agent OS", "create an action registry", "build a production agent system", "kernel with policy gate".
---

# Kernel Forge — WMAG Kernel Builder

Generates a **complete WMAG Kernel** (World Model + Action Graph):
a production-grade orchestration system where multiple agents share a
single, policy-enforced, idempotent runtime.

> **Built on Os-frame patterns.** References existing skills without modifications.
> For a single-agent first pass, start with `orchestra-forge` first.

---

## Architecture Overview

```
[User Request]
      ↓
  Kernel.task_send_subscribe()   ← async SSE entry point
      ↓
  WorldIndex → LLMPlanner        ← select & sequence actions
      ↓
  Policy Gate                    ← enforce roles + approval
      ↓
  ToolRunner (PocketFlow Nodes)  ← deterministic execution
      ↓
  Storage (idempotency cache)    ← persist + replay-safe
      ↓
  SSE stream → client            ← status + artifact events
```

**6 Ports (swappable adapters):**

| Port | Interface | Default Stub |
|------|-----------|--------------|
| `Storage` | Run/state persistence | In-memory dict |
| `Registry` | Tenant action catalog | JSON file |
| `WorldIndex` | Semantic action trees | Simple keyword match |
| `LLMPlanner` | Plan generation | LLM call (claude/gpt) |
| `ContextHydrator` | Context enrichment | Pass-through |
| `ToolRunner` | Action execution | PocketFlow nodes |

See [references/kernel-ports.md](references/kernel-ports.md) for full protocol specs.

---

## Phase 0 — SCOPE

**Goal**: Understand the system before touching any code.

Ask the user:

1. What is the **primary task** this kernel will handle? (e.g. customer support, code review, document processing)
2. How many **tenants** / user groups? What differs between them? (tools enabled, approval requirements, roles)
3. List 3-6 **actions** the kernel can take (e.g. `search_kb`, `draft_reply`, `escalate_ticket`)
4. Does any action need **human approval** before execution?
5. Is **streaming** (SSE) needed? Is this served via a web API?

Produce a **System Intent Card**:

```
System: <name>
Tenants: [tenant_a, tenant_b]
Actions: [action_1, action_2, action_3]
Approval-required: [action_X]
Streaming: yes/no
LLM Backend: claude-sonnet-4-5 | gpt-4o
```

**Checkpoint ✅** — Confirm intent card matches user vision.

---

## Phase 1 — REGISTRY

**Goal**: Define the action catalog in `registry.yaml`.

Generate `registry.yaml` from the intent card:

```yaml
schema_version: "1"
registry_id: "<system-name>-v1"

actions:
  - action_id: <action_id>
    tool: <tool_name>
    description: "<What this action does>"
    args_schema:
      type: object
      properties:
        <param>: {type: string, description: "<meaning>"}
      required: [<param>]
    security:
      requires_approval: false       # set true for high-risk actions
      allowed_roles: []              # [] = open to all roles

tool_contracts:
  - tool: <tool_name>
    endpoint: "stub"                 # replace with real endpoint

tenant_overrides:
  <tenant_id>:
    enabled_actions: [<action_id>]
    enabled_tools: [<tool_name>]
    security_overrides: []
```

See full template: [assets/registry.yaml.template](assets/registry.yaml.template)
See policy rules: [references/policy-gate.md](references/policy-gate.md)

**Checkpoint ✅** — Show `registry.yaml`, confirm actions + approval flags.

---

## Phase 2 — KERNEL

**Goal**: Generate the `kernel/` directory with all 6 ports as Python protocols + stubs.

### Directory Structure

```
kernel/
├── __init__.py
├── flow.py                    ← Kernel dataclass + task_send_subscribe()
├── ports/
│   ├── storage.py             ← Protocol
│   ├── registry.py            ← Protocol
│   ├── index.py               ← Protocol
│   ├── planner.py             ← Protocol
│   ├── hydrator.py            ← Protocol
│   └── toolrunner.py          ← Protocol
├── adapters/
│   ├── mem_storage.py         ← in-memory Storage stub
│   ├── json_registry.py       ← JSON file Registry stub
│   ├── keyword_index.py       ← keyword WorldIndex stub
│   ├── llm_planner.py         ← LLM-backed Planner
│   └── pf_toolrunner.py       ← PocketFlow ToolRunner ← see Phase 3
└── runtime/
    ├── events.py              ← status_event(), artifact_event()
    ├── idempotency.py         ← SHA-256 idempotency key
    ├── policy.py              ← policy_gate_plan()
    ├── retry.py               ← exponential backoff
    └── validation.py          ← validate_task_input()
```

### `kernel/flow.py` pattern

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict

@dataclass
class Kernel:
    storage: Storage
    registry: RegistryProvider
    index: WorldIndexProvider
    planner: LLMPlanner
    hydrator: ContextHydrator
    tools: ToolRunner

    async def task_send_subscribe(
        self, task_input: Dict[str, Any]
    ) -> AsyncIterator[Dict[str, Any]]:
        validate_task_input(task_input)
        run = await self.storage.create_or_load_run(
            task_id=task_input["task_id"],
            tenant_id=task_input["tenant_id"]
        )
        run_id = run["run_id"]

        yield status_event(task_input["task_id"], run_id, "submitted", "Accepted")

        # ... plan → gate → execute → stream results
        # See full flow in references/kernel-ports.md
```

See SSE streaming guide: [references/sse-streaming.md](references/sse-streaming.md)

**Checkpoint ✅** — Show full `kernel/` structure. Ask: "Replace any stub with a real adapter now, or continue to wiring?"

---

## Phase 3 — WIRE (PocketFlow ToolRunner)

**Goal**: Implement the `ToolRunner` using PocketFlow nodes (from `pocketflow` skill).

Copy engine: [../pocketflow/scripts/pocketflow.py](../pocketflow/scripts/pocketflow.py)

For each action in the registry, create a PocketFlow `Node`:

```python
# kernel/adapters/pf_toolrunner.py
from pocketflow import Node, Flow

class <ActionName>Node(Node):
    def prep(self, shared):
        return shared["step_args"]

    def exec(self, args):
        # actual work: LLM call, API call, DB query
        return do_work(args)

    def post(self, shared, prep_res, exec_res):
        shared["step_result"] = exec_res
        return "default"

# ToolRunner adapter wires action_id → Node class
ACTION_MAP = {
    "<action_id>": <ActionName>Node,
}

class PocketFlowToolRunner:
    async def run_step(self, step, args, shared):
        node_cls = ACTION_MAP[step["action_id"]]
        node = node_cls(max_retries=step.get("retries", 2))
        flow = Flow(start=node)
        flow.run(shared | {"step_args": args})
        return shared.get("step_result")
```

For deep node patterns, see: [../num-agents/references/flow-patterns.md](../num-agents/references/flow-patterns.md)

**Checkpoint ✅** — Show `pf_toolrunner.py`. Confirm all registry actions are wired.

---

## Phase 4 — FORGE (Audit)

Run 5-role Skill Architect pipeline on the generated system:

| Role | What to check |
|------|---------------|
| Architecture Analyst | All 6 ports implemented? Registry covers all wired actions? |
| Code Refactorer | Idempotency keys on every step? Retries on LLM nodes? |
| Skill Reviewer | SSE yields at each state transition? Storage not skipped? |
| Security Auditor | Prompt injection via `user_message`? Hardcoded secrets? Role bypass? |
| Doc Enhancer | Docstrings on all adapters. Usage example. ENV vars documented. |

Role checklists: [../skill-architect/references/agent-roles.md](../skill-architect/references/agent-roles.md)

**Final summary:**

```
## ✅ Kernel Forge — Complete

| Phase | Status | Output |
|-------|--------|--------|
| Scope | ✅ | System Intent Card |
| Registry | ✅ | registry.yaml |
| Kernel | ✅ | kernel/ (6 ports + adapters + runtime) |
| Wire | ✅ | pf_toolrunner.py |
| Forge | ✅ | Audited + hardened system |
```

---

## Output Checklist

- [ ] `registry.yaml` — action catalog + tenant policies
- [ ] `pocketflow.py` — execution engine (copied)
- [ ] `kernel/flow.py` — Kernel dataclass + SSE loop
- [ ] `kernel/ports/*.py` — 6 Protocol interfaces
- [ ] `kernel/adapters/*.py` — stubs + PocketFlow ToolRunner
- [ ] `kernel/runtime/*.py` — events, idempotency, policy, retry
- [ ] Forge audit passed

---

## References

- Kernel port specs: [references/kernel-ports.md](references/kernel-ports.md)
- Policy Gate & idempotency: [references/policy-gate.md](references/policy-gate.md)
- SSE streaming: [references/sse-streaming.md](references/sse-streaming.md)
- Universe selection: [../num-agents/references/universe-catalog.md](../num-agents/references/universe-catalog.md)
- PocketFlow engine: [../pocketflow/scripts/pocketflow.py](../pocketflow/scripts/pocketflow.py)
- Skill Architect audit: [../skill-architect/references/agent-roles.md](../skill-architect/references/agent-roles.md)
- Example kernel: [examples/support-kernel.md](examples/support-kernel.md)
