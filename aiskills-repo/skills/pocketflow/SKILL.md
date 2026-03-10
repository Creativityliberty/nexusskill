---
name: pocketflow
description: Build LLM-powered workflows using the PocketFlow framework — a minimalist Python library for chaining AI nodes into graphs and pipelines. Use when the user wants to create an AI agent, multi-step LLM pipeline, agentic loop, batch processing workflow, or async AI flow. Triggers on "build a pocketflow", "create an AI workflow", "make an agent with pocketflow", "pocketflow".
---

# PocketFlow Skill

PocketFlow is a ~100-line Python framework for building LLM workflows as graphs of nodes.
The library is bundled at `scripts/pocketflow.py` — copy it into the user's project.

## Core Concepts

```
shared    ← dict passed through all nodes (global state)
Node      ← single step: prep → exec → post
Flow      ← graph of nodes with conditional transitions
BatchNode ← process a list of items through one node
```

### Node Lifecycle

```python
def prep(self, shared):   # read from shared, return prep_res
def exec(self, prep_res): # do the work (LLM call, API, etc.), return exec_res
def post(self, shared, prep_res, exec_res):  # write to shared, return action string
```

`post` returns an **action string** that determines the next node in the flow (`"default"`, `"retry"`, `"done"`, etc.).

## Node Types

| Class | Use case |
|-------|----------|
| `Node` | Single step with optional retries |
| `BatchNode` | Run exec() on a list of items |
| `Flow` | Orchestrate nodes into a graph |
| `BatchFlow` | Run a flow for each item in a batch |
| `AsyncNode` | Async version of Node |
| `AsyncBatchNode` | Async batch processing |
| `AsyncParallelBatchNode` | Parallel async batch (asyncio.gather) |
| `AsyncFlow` | Async orchestrator |

## Usage Pattern

### 1. Copy the Library

```bash
cp path/to/skills/pocketflow/scripts/pocketflow.py ./pocketflow.py
```

### 2. Build Nodes

```python
from pocketflow import Node, Flow

class FetchData(Node):
    def prep(self, shared):
        return shared["query"]

    def exec(self, query):
        # call LLM or API
        return call_llm(query)

    def post(self, shared, prep_res, exec_res):
        shared["result"] = exec_res
        return "default"  # next node

class Validate(Node):
    def exec(self, prep_res):
        return check_quality(prep_res)

    def post(self, shared, prep_res, exec_res):
        return "done" if exec_res else "retry"
```

### 3. Wire the Flow

```python
fetch = FetchData(max_retries=3, wait=1)
validate = Validate()

# Linear: fetch → validate
fetch >> validate

# Conditional: validate → fetch (retry) or end (done)
validate - "retry" >> fetch

flow = Flow(start=fetch)
```

### 4. Run

```python
shared = {"query": "What is the capital of France?"}
flow.run(shared)
print(shared["result"])
```

## Retry Pattern

```python
class RobustLLMCall(Node):
    def __init__(self):
        super().__init__(max_retries=3, wait=2)  # 3 attempts, 2s between

    def exec(self, prompt):
        return call_llm(prompt)  # raises on failure → auto retry

    def exec_fallback(self, prep_res, exc):
        return "fallback response"  # last resort
```

## Async Pattern

```python
from pocketflow import AsyncNode, AsyncFlow

class AsyncLLMNode(AsyncNode):
    async def exec_async(self, prompt):
        return await async_llm_call(prompt)

    async def post_async(self, shared, prep_res, exec_res):
        shared["result"] = exec_res
        return "default"

node = AsyncLLMNode()
flow = AsyncFlow(start=node)

# Run:
import asyncio
asyncio.run(flow.run_async(shared))
```

## Parallel Batch Pattern

```python
from pocketflow import AsyncParallelBatchNode, AsyncFlow

class ParallelSummarizer(AsyncParallelBatchNode):
    async def exec_async(self, doc):
        return await summarize(doc)

node = ParallelSummarizer()

class LoadDocs(AsyncNode):
    async def prep_async(self, shared):
        return shared["docs"]  # list of documents
    async def post_async(self, shared, prep_res, exec_res):
        # exec_res is gathered list of results
        shared["summaries"] = exec_res
        return "default"
```

## Workflow for Building a PocketFlow App

1. **Copy** `scripts/pocketflow.py` into the project
2. **Map the workflow** — identify each distinct step as a node
3. **Design shared** — define what data flows through (keys in shared dict)
4. **Implement nodes** — one class per step
5. **Wire transitions** — `>>` for linear, `- "action" >>` for conditional
6. **Choose async** if making parallel LLM calls
7. **Add retries** on unreliable nodes (LLM calls, APIs)
8. **Test** with `flow.run(shared)` and inspect shared dict after

## Operator Shortcuts

```python
a >> b            # a connects to b on "default" action
a - "retry" >> b  # a connects to b on "retry" action
```
