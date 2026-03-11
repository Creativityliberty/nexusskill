# SSE Streaming Reference

The Kernel streams real-time events to the client using Server-Sent Events (SSE)
via Python `AsyncIterator`. Every state transition yields an event.

---

## Event Types

### `status_event`

Signals a lifecycle state change.

```python
def status_event(task_id, run_id, state, message, meta=None):
    return {
        "type": "status",
        "task_id": task_id,
        "run_id": run_id,
        "state": state,          # submitted | working | input-required | completed | failed | canceled
        "message": message,
        "meta": meta or {}
    }
```

### `artifact_event`

Delivers a named payload (plan, step result, final output).

```python
def artifact_event(task_id, run_id, name, data):
    return {
        "type": "artifact",
        "task_id": task_id,
        "run_id": run_id,
        "name": name,            # "plan" | "step_result" | "final"
        "data": data
    }
```

---

## State Machine

```
submitted → working → [input-required →] working → completed
                                                  → failed
                                                  → canceled
```

| Yield point | State | Event |
| :--- | :--- | :--- |
| Task received | `submitted` | `status_event` |
| Planning started | `working` | `status_event` |
| Plan ready | — | `artifact_event("plan", plan)` |
| Approval needed | `input-required` | `status_event` + meta=report |
| Approved | `working` | `status_event` |
| Each step done | — | `artifact_event("step_result", r)` |
| All done | `completed` or `failed` | `status_event` |

---

## FastAPI SSE Integration

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

@app.post("/tasks/send-subscribe")
async def send_subscribe(task_input: dict):
    kernel = build_kernel()  # inject your adapters

    async def event_generator():
        async for event in kernel.task_send_subscribe(task_input):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### Client-side (JavaScript)

```javascript
const source = new EventSource('/tasks/send-subscribe');
source.onmessage = (e) => {
    const event = JSON.parse(e.data);
    if (event.type === 'status') console.log(event.state, event.message);
    if (event.type === 'artifact') console.log(event.name, event.data);
    if (event.state === 'completed' || event.state === 'failed') source.close();
};
```

---

## Rules

- ✅ Always yield `submitted` before any async work
- ✅ Always yield `completed` or `failed` as the last event
- ✅ Yield `artifact_event("step_result", r)` for each executed step
- ❌ Never return without yielding a terminal state event
- ❌ Never yield `None` — always construct events with both helper functions
