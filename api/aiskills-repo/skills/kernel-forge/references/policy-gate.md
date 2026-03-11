# Policy Gate & Idempotency

## Policy Gate

The policy gate enforces **tenant-scoped** security rules before executing any plan.

### How it works

```python
from kernel.runtime.policy import policy_gate_plan

needs_approval, report = policy_gate_plan(
    ctx={"tenant": tenant_ctx, "registry": reg},
    plan=plan
)

if report.get("fatal"):
    # Violations found — stop execution
    yield status_event(task_id, run_id, "failed", "Policy gate failed", meta=report)
    return

if needs_approval:
    # Pause and wait for human approval
    yield status_event(task_id, run_id, "input-required", "Approval required", meta=report)
    # ... wait and check decision
```

### Policy rules (in `registry.yaml`)

```yaml
actions:
  - action_id: escalate_ticket
    security:
      requires_approval: true       # ← triggers approval flow
      allowed_roles: ["manager"]    # ← only managers can trigger this
```

### Tenant overrides

Override policies per tenant without editing the base registry:

```yaml
tenant_overrides:
  enterprise:
    enabled_actions: [search_kb, draft_reply, escalate_ticket]
    security_overrides:
      - action_id: escalate_ticket
        set:
          - path: /security/requires_approval
            value: false             # enterprise: no approval needed
  free:
    enabled_actions: [search_kb]     # free: search only
```

### Violations vs. Approval

| Outcome | Cause | Behavior |
| :--- | :--- | :--- |
| `fatal: true` | Role mismatch or action not in allowed list | Immediately fail, yield `status=failed` |
| `needs_approval: true` | Action has `requires_approval: true` | Pause, yield `status=input-required`, wait |
| Clean pass | No violations, no approval needed | Continue to execution |

---

## Idempotency

Every step execution is keyed by a SHA-256 hash of its full context. If the kernel crashes and replays, steps already executed are **not re-run**.

### Key computation

```python
from kernel.runtime.idempotency import compute_idempotency_key

idem_key = compute_idempotency_key(
    tenant_id=task_input["tenant_id"],
    run_id=run_id,
    step_id=step["step_id"],
    action_id=step["action_id"],
    args=step.get("args", {})
)
```

Implementation (SHA-256 of stable JSON):

```python
import hashlib, json

def compute_idempotency_key(*, tenant_id, run_id, step_id, action_id, args):
    payload = {"tenant_id": tenant_id, "run_id": run_id,
               "step_id": step_id, "action_id": action_id, "args": args}
    h = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return "idem_" + h[:32]
```

### Usage in ToolRunner

```python
cached = await storage.get_step_result(idem_key)
if cached:
    return cached  # replay-safe: return cached result

result = await tools.run_step(step, args, shared)
await storage.save_step_result(idem_key, result)
return result
```

### Rules

- ✅ Always compute idempotency key before executing a step
- ✅ Always check cache before calling ToolRunner
- ✅ Always save result after execution
- ❌ Never mutate `args` after key computation (would break cache lookup)
