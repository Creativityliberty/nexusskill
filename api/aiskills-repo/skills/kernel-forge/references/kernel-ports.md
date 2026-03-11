# Kernel Ports — Protocol Reference

## Table of Contents

1. [Storage](#storage)
2. [RegistryProvider](#registryprovider)
3. [WorldIndexProvider](#worldindexprovider)
4. [LLMPlanner](#llmplanner)
5. [ContextHydrator](#contexthydrator)
6. [ToolRunner](#toolrunner)

---

## Storage

Persists run state, approval requests, and step results (idempotency cache).

```python
from typing import Any, Dict, Optional, Protocol

class Storage(Protocol):
    async def create_or_load_run(self, task_id: str, tenant_id: str) -> Dict[str, Any]: ...
    async def set_run_state(self, run_id: str, state: str) -> None: ...
    async def persist_update(self, run_id: str, update: Dict[str, Any]) -> None: ...
    async def load_tenant_context(self, tenant_id: str) -> Dict[str, Any]: ...
    async def create_approval_request(self, run_id: str, payload: Dict[str, Any]) -> str: ...
    async def wait_for_approval(self, approval_id: str) -> Dict[str, Any]: ...
    async def get_step_result(self, idem_key: str) -> Optional[Dict[str, Any]]: ...
    async def save_step_result(self, idem_key: str, step_result: Dict[str, Any]) -> None: ...
```

**In-memory stub** (`adapters/mem_storage.py`):

```python
import asyncio, uuid

class MemStorage:
    def __init__(self):
        self._runs = {}
        self._idem = {}
        self._approvals = {}

    async def create_or_load_run(self, task_id, tenant_id):
        run_id = str(uuid.uuid4())
        self._runs[run_id] = {"run_id": run_id, "task_id": task_id, "tenant_id": tenant_id, "state": "init"}
        return self._runs[run_id]

    async def get_step_result(self, idem_key):
        return self._idem.get(idem_key)

    async def save_step_result(self, idem_key, result):
        self._idem[idem_key] = result
    # ... other methods as needed
```

---

## RegistryProvider

Loads the tenant-specific action catalog from a source (JSON file, DB, etc.).

```python
class RegistryProvider(Protocol):
    async def load_registry(self, tenant_id: str) -> Dict[str, Any]: ...
```

**JSON file stub** (`adapters/json_registry.py`):

```python
import json, pathlib

class JsonRegistry:
    def __init__(self, path: str):
        self._data = json.loads(pathlib.Path(path).read_text())

    async def load_registry(self, tenant_id: str) -> Dict[str, Any]:
        from kernel.runtime.policy import apply_tenant_overrides
        return apply_tenant_overrides(self._data, tenant_id)
```

---

## WorldIndexProvider

Builds semantic trees of actions to help the planner select relevant ones.

```python
class WorldIndexProvider(Protocol):
    async def load_or_build_trees(self, tenant_id: str, domains: list[str]) -> Dict[str, Any]: ...
```

**Keyword stub** (`adapters/keyword_index.py`):

```python
class KeywordIndex:
    async def load_or_build_trees(self, tenant_id, domains):
        # Returns a flat dict mapping domain → action_ids
        # Replace with vector search (e.g. Sentence Transformers) for production
        return {d: [] for d in domains}
```

---

## LLMPlanner

Selects actions and builds an execution plan from context.

```python
class LLMPlanner(Protocol):
    async def select_nodes(self, user_message: str, trees: Dict, policies: list) -> list: ...
    async def build_plan(self, pack: Dict) -> Dict: ...
```

**LLM stub** (`adapters/llm_planner.py`):

```python
import json

class LLMBackedPlanner:
    def __init__(self, call_llm):
        self._call = call_llm   # async fn(prompt: str) -> str

    async def select_nodes(self, user_message, trees, policies):
        # Ask LLM which action_ids are relevant
        prompt = f"Given: '{user_message}'\nAvailable actions: {trees}\nList action_ids to use (JSON array):"
        resp = await self._call(prompt)
        return json.loads(resp)

    async def build_plan(self, pack):
        prompt = f"Build an execution plan for: {json.dumps(pack)}\nReturn JSON with 'steps' array."
        resp = await self._call(prompt)
        return json.loads(resp)
```

---

## ContextHydrator

Enriches the user message + node list with tenant registry context before planning.

```python
class ContextHydrator(Protocol):
    async def hydrate(self, tenant_id: str, user_message: str, node_list: list, registry: Dict) -> Dict: ...
```

**Pass-through stub** (`adapters/passthrough_hydrator.py`):

```python
class PassthroughHydrator:
    async def hydrate(self, tenant_id, user_message, node_list, registry):
        return {
            "tenant_id": tenant_id,
            "user_message": user_message,
            "nodes": node_list,
            "registry": registry,
        }
```

---

## ToolRunner

Executes a single plan step. Implemented as PocketFlow nodes in Phase 3.

```python
class ToolRunner(Protocol):
    async def run_step(self, step: Dict, args: Dict, shared: Dict) -> Dict: ...
```

**PocketFlow adapter** → see Phase 3 of SKILL.md and `adapters/pf_toolrunner.py`.
