# Flow Patterns

## Table of Contents
1. [Node Basics](#node-basics)
2. [SharedStore](#sharedstore)
3. [Linear Flow](#linear-flow)
4. [Retry & Error Handling](#retry--error-handling)
5. [Execution Hooks](#execution-hooks)
6. [Conditional Nodes](#conditional-nodes)
7. [Async Nodes](#async-nodes)
8. [Batch Processing](#batch-processing)
9. [Flow Serialization](#flow-serialization)
10. [Full Example](#full-example)

---

## Node Basics

```python
from num_agents import Node, SharedStore

class MyNode(Node):
    def __init__(self):
        super().__init__(
            name="StepName",       # display name
            retry_count=1,         # attempts before failing (default: 1)
            enable_logging=True    # structured logs
        )

    def exec(self, shared: SharedStore):
        # Read inputs
        value = shared.get("key", default_value)

        # Do work
        result = process(value)

        # Write outputs
        shared.set("output_key", result)

        return result  # returned value stored in flow results
```

---

## SharedStore

```python
shared = SharedStore()

shared.set("key", value)
value = shared.get("key")
value = shared.get("key", "default")  # with default
shared.delete("key")
all_data = shared.to_dict()           # export as plain dict
```

**Convention**: use snake_case keys. Document expected keys in node docstrings.

---

## Linear Flow

```python
from num_agents import Flow

# Create nodes
fetch = FetchNode()
process = ProcessNode()
save = SaveNode()

# Wire: fetch → process → save
fetch.connect(process)
process.connect(save)

# Build flow
flow = Flow(name="DataPipeline", enable_logging=True)
flow.add_node(fetch)
flow.add_node(process)
flow.add_node(save)
flow.set_start(fetch)

# Run
results = flow.execute(initial_data={"url": "https://..."})
```

---

## Retry & Error Handling

```python
class UnstableAPINode(Node):
    def __init__(self):
        super().__init__(
            name="APICall",
            retry_count=3       # 3 attempts, exponential backoff
        )

    def exec(self, shared: SharedStore):
        response = call_api()   # raises on failure → auto retry
        shared.set("response", response)
        return response

    def on_retry(self, attempt: int, error: Exception, shared: SharedStore):
        """Called before each retry (optional override)."""
        logger.warning(f"Attempt {attempt} failed: {error}")

    def on_failure(self, error: Exception, shared: SharedStore):
        """Called when all retries exhausted (optional override)."""
        shared.set("error", str(error))
        raise error  # or return fallback value
```

---

## Execution Hooks

```python
import time
import logging

logger = logging.getLogger(__name__)

node = MyNode()

# Before hook — runs before exec()
node.add_before_hook(
    lambda shared: shared.set("start_time", time.time())
)

# After hook — runs after exec() succeeds
node.add_after_hook(
    lambda shared, result: shared.set(
        "duration_ms",
        (time.time() - shared.get("start_time")) * 1000
    )
)

# Error hook — runs when exec() raises
node.add_error_hook(
    lambda shared, error: logger.error(
        f"[{node.name}] failed: {error}",
        extra={"shared": shared.to_dict()}
    )
)
```

---

## Conditional Nodes

```python
from num_agents import ConditionalNode

# Define the condition
def is_high_value(shared: SharedStore) -> bool:
    return shared.get("score", 0) > 100

# Create branches
high_path = HighValueProcessorNode()
low_path = LowValueProcessorNode()

# Wire conditional
router = ConditionalNode(
    condition=is_high_value,
    true_node=high_path,
    false_node=low_path
)

# Add to flow
flow.add_node(router)
flow.add_node(high_path)
flow.add_node(low_path)
prev_node.connect(router)
```

### Multi-branch routing

```python
from num_agents import RouterNode

def route_by_type(shared: SharedStore) -> str:
    return shared.get("document_type", "unknown")

router = RouterNode(
    selector=route_by_type,
    routes={
        "invoice": invoice_node,
        "contract": contract_node,
        "email": email_node,
    },
    default=generic_node   # fallback if no match
)
```

---

## Async Nodes

```python
from num_agents import AsyncNode

class AsyncAPINode(AsyncNode):
    def __init__(self):
        super().__init__(name="AsyncFetch", retry_count=3)

    async def exec(self, shared: SharedStore):
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(shared.get("url")) as resp:
                data = await resp.json()
                shared.set("data", data)
                return data

# Run async flow
from num_agents import AsyncFlow
import asyncio

flow = AsyncFlow(name="AsyncPipeline")
flow.add_node(async_node)
flow.set_start(async_node)

results = asyncio.run(flow.execute_async(initial_data={"url": "..."}))
```

---

## Batch Processing

```python
from num_agents import BatchNode

class SummarizeNode(BatchNode):
    """Processes a list of documents, one at a time."""

    def exec(self, shared: SharedStore):
        documents = shared.get("documents", [])
        summaries = []
        for doc in documents:
            summaries.append(summarize(doc))
        shared.set("summaries", summaries)
        return summaries
```

---

## Flow Serialization

```python
# Save flow config
flow.save("pipeline_config.json")

# Load and restore
from num_agents import Flow
flow = Flow.load("pipeline_config.json")
results = flow.execute(initial_data={...})
```

---

## Full Example

```python
from num_agents import Node, Flow, ConditionalNode, SharedStore
from num_agents import configure_logging
import logging, time

configure_logging(level=logging.INFO)

class FetchNode(Node):
    def __init__(self):
        super().__init__(name="Fetch", retry_count=3, enable_logging=True)

    def exec(self, shared: SharedStore):
        data = fetch_data(shared.get("source_url"))
        shared.set("raw_data", data)
        shared.set("item_count", len(data))
        return data

class ClassifyNode(Node):
    def __init__(self):
        super().__init__(name="Classify", enable_logging=True)

    def exec(self, shared: SharedStore):
        score = classify(shared.get("raw_data"))
        shared.set("score", score)
        return score

class HighValueNode(Node):
    def exec(self, shared: SharedStore):
        result = process_high_value(shared.get("raw_data"))
        shared.set("result", result)
        return result

class LowValueNode(Node):
    def exec(self, shared: SharedStore):
        result = process_low_value(shared.get("raw_data"))
        shared.set("result", result)
        return result

# Wire
fetch = FetchNode()
classify = ClassifyNode()
router = ConditionalNode(
    condition=lambda s: s.get("score", 0) > 50,
    true_node=HighValueNode(),
    false_node=LowValueNode()
)

fetch.connect(classify)
classify.connect(router)

# Hooks
fetch.add_before_hook(lambda s: s.set("t0", time.time()))
fetch.add_after_hook(lambda s, r: s.set("fetch_ms", (time.time()-s.get("t0"))*1000))

# Run
flow = Flow(name="ClassificationPipeline", enable_logging=True)
for n in [fetch, classify, router.true_node, router.false_node]:
    flow.add_node(n)
flow.add_node(router)
flow.set_start(fetch)

results = flow.execute(initial_data={"source_url": "https://api.example.com/data"})
print(results)
```
