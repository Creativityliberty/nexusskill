"""
Flow Orchestrator Runtime
=========================
Wraps PocketFlow Flows with pause/resume/snapshot/trace capabilities.

Usage:
    from orchestrator import OrchestratorRuntime
    runtime = OrchestratorRuntime(flow, enable_trace=True)
    runtime.run(shared)
"""

import asyncio
import json
import time
import threading
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Traced Node Wrapper
# ---------------------------------------------------------------------------

class TracedNodeMixin:
    """Mixin that adds tracing to any PocketFlow Node."""

    def _trace_event(self, event_type, node_name, data=None):
        if hasattr(self, '_tracer') and self._tracer:
            self._tracer.log(event_type, node_name, data)

    def _check_pause(self):
        if hasattr(self, '_pause_event') and self._pause_event:
            while self._pause_event.is_set():
                time.sleep(0.1)


# ---------------------------------------------------------------------------
# Orchestrator Runtime
# ---------------------------------------------------------------------------

class OrchestratorRuntime:
    """
    Production-grade runtime wrapper for PocketFlow pipelines.
    
    Features:
        - Pause / Resume execution between nodes
        - State snapshots for rollback
        - Execution tracing with timestamps
        - Status monitoring
    
    Example:
        >>> from pocketflow import Flow
        >>> runtime = OrchestratorRuntime(my_flow, enable_trace=True)
        >>> runtime.run(shared_data)
        >>> runtime.pause()   # freeze after current node
        >>> runtime.resume()  # continue
        >>> runtime.tracer.export("trace.json")
    """

    def __init__(self, flow, enable_trace=True, enable_snapshots=True, 
                 snapshot_dir=".snapshots"):
        self.flow = flow
        self.enable_trace = enable_trace
        self.enable_snapshots = enable_snapshots
        
        # State
        self._paused = threading.Event()
        self._running = False
        self._current_node = None
        self._start_time = None
        self._end_time = None
        
        # Tracer
        self.tracer = Tracer() if enable_trace else None
        
        # Snapshot manager
        self.snapshots = SnapshotManager(snapshot_dir) if enable_snapshots else None
        
        # Inject tracing into flow nodes
        if enable_trace:
            self._inject_tracing(flow)

    def _inject_tracing(self, flow):
        """Inject tracing hooks into all nodes in the flow."""
        visited = set()
        self._walk_and_inject(flow, visited)

    def _walk_and_inject(self, node, visited):
        """Recursively walk the flow graph and inject tracing."""
        if id(node) in visited:
            return
        visited.add(id(node))
        
        # Store reference to tracer and pause event
        node._tracer = self.tracer
        node._pause_event = self._paused
        node._runtime = self
        
        # Wrap the original run method
        original_run = node.run.__func__ if hasattr(node.run, '__func__') else node.run
        runtime_ref = self
        
        def traced_run(self_node, shared):
            node_name = type(self_node).__name__
            
            # Check pause before each node
            while runtime_ref._paused.is_set():
                time.sleep(0.1)
            
            runtime_ref._current_node = node_name
            
            # Snapshot before node if enabled
            if runtime_ref.snapshots and runtime_ref.enable_snapshots:
                runtime_ref.snapshots.save(
                    shared, 
                    label=f"before_{node_name}_{int(time.time())}",
                    auto=True
                )
            
            # Trace entry
            if runtime_ref.tracer:
                runtime_ref.tracer.log("node_enter", node_name, {
                    "shared_keys": list(shared.keys()) if isinstance(shared, dict) else "N/A"
                })
            
            try:
                result = original_run(self_node, shared)
                
                # Trace exit
                if runtime_ref.tracer:
                    runtime_ref.tracer.log("node_exit", node_name, {
                        "action": result,
                        "shared_keys": list(shared.keys()) if isinstance(shared, dict) else "N/A"
                    })
                
                return result
                
            except Exception as e:
                if runtime_ref.tracer:
                    runtime_ref.tracer.log("node_error", node_name, {
                        "error": str(e),
                        "type": type(e).__name__
                    })
                raise
        
        # Only patch if not already patched
        if not getattr(node, '_traced', False):
            import types
            node.run = types.MethodType(traced_run, node)
            node._traced = True
        
        # Walk successors
        if hasattr(node, 'successors'):
            for successor in node.successors.values():
                self._walk_and_inject(successor, visited)
        
        # Walk nested flow start node
        if hasattr(node, 'start') and node.start:
            self._walk_and_inject(node.start, visited)

    def run(self, shared):
        """Run the orchestrated pipeline."""
        self._running = True
        self._start_time = time.time()
        self._current_node = "start"
        
        if self.tracer:
            self.tracer.log("pipeline_start", "OrchestratorRuntime", {
                "flow": type(self.flow).__name__,
                "timestamp": datetime.now().isoformat()
            })
        
        try:
            result = self.flow.run(shared)
            
            if self.tracer:
                self.tracer.log("pipeline_end", "OrchestratorRuntime", {
                    "duration_s": round(time.time() - self._start_time, 2),
                    "result": str(result)
                })
            
            return result
        
        except Exception as e:
            if self.tracer:
                self.tracer.log("pipeline_error", "OrchestratorRuntime", {
                    "error": str(e),
                    "duration_s": round(time.time() - self._start_time, 2)
                })
            raise
        
        finally:
            self._running = False
            self._end_time = time.time()

    def pause(self):
        """Pause execution after current node completes."""
        self._paused.set()
        if self.tracer:
            self.tracer.log("runtime_pause", self._current_node or "unknown")
        print(f"⏸️  Orchestrator paused at node: {self._current_node}")

    def resume(self):
        """Resume execution from pause point."""
        self._paused.clear()
        if self.tracer:
            self.tracer.log("runtime_resume", self._current_node or "unknown")
        print(f"▶️  Orchestrator resumed from node: {self._current_node}")

    def status(self):
        """Get current runtime status."""
        elapsed = time.time() - self._start_time if self._start_time else 0
        return {
            "running": self._running,
            "paused": self._paused.is_set(),
            "current_node": self._current_node,
            "elapsed_seconds": round(elapsed, 2),
            "trace_events": len(self.tracer.events) if self.tracer else 0,
            "snapshots": self.snapshots.list() if self.snapshots else []
        }


# ---------------------------------------------------------------------------
# Tracer
# ---------------------------------------------------------------------------

class Tracer:
    """
    Execution tracer that logs node transitions with timestamps.
    
    Outputs:
        - JSON log file
        - Mermaid diagram of execution flow
        - Human-readable summary
    """

    def __init__(self):
        self.events = []
        self._start = time.time()

    def log(self, event_type, node_name, data=None):
        """Log a trace event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": round((time.time() - self._start) * 1000, 1),
            "event": event_type,
            "node": node_name,
            "data": data or {}
        }
        self.events.append(event)

    def export(self, filepath):
        """Export trace to JSON file."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"trace": self.events}, f, indent=2, default=str)
        print(f"📊 Trace exported to {path}")

    def to_mermaid(self, filepath=None):
        """Generate a Mermaid sequence diagram from trace events."""
        lines = ["sequenceDiagram"]
        lines.append("    participant R as Runtime")
        
        # Collect unique nodes
        nodes = []
        for e in self.events:
            if e["node"] not in nodes and e["node"] != "OrchestratorRuntime":
                nodes.append(e["node"])
        
        for n in nodes:
            lines.append(f"    participant {n}")
        
        prev_node = "R"
        for e in self.events:
            node = e["node"]
            if node == "OrchestratorRuntime":
                node = "R"
            
            if e["event"] == "node_enter":
                lines.append(f"    R->>+{node}: exec ({e['elapsed_ms']}ms)")
            elif e["event"] == "node_exit":
                action = e.get("data", {}).get("action", "default")
                lines.append(f"    {node}-->>-R: {action}")
            elif e["event"] == "node_error":
                err = e.get("data", {}).get("type", "Error")
                lines.append(f"    {node}--x R: ❌ {err}")
            elif e["event"] == "runtime_pause":
                lines.append(f"    Note over R: ⏸️ PAUSED")
            elif e["event"] == "runtime_resume":
                lines.append(f"    Note over R: ▶️ RESUMED")
        
        mermaid = "\n".join(lines)
        
        if filepath:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"```mermaid\n{mermaid}\n```\n")
            print(f"📊 Mermaid diagram exported to {path}")
        
        return mermaid

    def summary(self):
        """Print a human-readable execution summary."""
        print("\n" + "=" * 60)
        print("  EXECUTION TRACE SUMMARY")
        print("=" * 60)
        
        node_times = {}
        for e in self.events:
            if e["event"] == "node_enter":
                node_times[e["node"]] = e["elapsed_ms"]
            elif e["event"] == "node_exit" and e["node"] in node_times:
                duration = e["elapsed_ms"] - node_times[e["node"]]
                print(f"  ✓ {e['node']:30s} {duration:8.1f}ms  → {e['data'].get('action', 'default')}")
                del node_times[e["node"]]
        
        total = self.events[-1]["elapsed_ms"] if self.events else 0
        print(f"\n  Total: {total:.1f}ms | Events: {len(self.events)}")
        print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Snapshot Manager
# ---------------------------------------------------------------------------

class SnapshotManager:
    """
    Manage state snapshots for rollback and debugging.
    
    Usage:
        sm = SnapshotManager(".snapshots")
        sm.save(shared, "checkpoint_1")
        shared = sm.load("checkpoint_1")
    """

    def __init__(self, directory=".snapshots"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._auto_count = 0
        self._max_auto = 20  # Max auto-snapshots to keep

    def save(self, shared, label, auto=False):
        """Save a snapshot of shared data."""
        if auto:
            self._auto_count += 1
            if self._auto_count > self._max_auto:
                return  # Skip to avoid disk bloat
        
        # Filter non-serializable items
        serializable = {}
        for k, v in shared.items():
            if k.startswith("__snapshot_exclude__"):
                continue
            try:
                json.dumps(v, default=str)
                serializable[k] = v
            except (TypeError, ValueError):
                serializable[k] = f"<non-serializable: {type(v).__name__}>"
        
        snapshot = {
            "label": label,
            "timestamp": datetime.now().isoformat(),
            "auto": auto,
            "data": serializable
        }
        
        filepath = self.directory / f"{label}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, default=str)
        
        if not auto:
            print(f"📸 Snapshot saved: {label}")

    def load(self, label):
        """Load a snapshot and return the shared data."""
        filepath = self.directory / f"{label}.json"
        if not filepath.exists():
            raise FileNotFoundError(f"Snapshot '{label}' not found at {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            snapshot = json.load(f)
        
        print(f"🔄 Snapshot restored: {label} (from {snapshot['timestamp']})")
        return snapshot["data"]

    def list(self):
        """List all available snapshots."""
        snapshots = []
        for f in sorted(self.directory.glob("*.json")):
            try:
                with open(f, 'r', encoding='utf-8') as fh:
                    s = json.load(fh)
                if not s.get("auto", False):  # Hide auto snapshots
                    snapshots.append({
                        "label": s["label"],
                        "timestamp": s["timestamp"],
                        "file": str(f)
                    })
            except (json.JSONDecodeError, KeyError):
                continue
        return snapshots

    def diff(self, label_a, label_b):
        """Compare two snapshots and show differences."""
        data_a = self.load(label_a)
        data_b = self.load(label_b)
        
        all_keys = set(list(data_a.keys()) + list(data_b.keys()))
        changes = {}
        
        for key in sorted(all_keys):
            val_a = data_a.get(key, "<missing>")
            val_b = data_b.get(key, "<missing>")
            if str(val_a) != str(val_b):
                changes[key] = {"before": val_a, "after": val_b}
        
        print(f"\n📊 Diff: {label_a} → {label_b}")
        print(f"   Changed keys: {len(changes)} / {len(all_keys)}")
        for k, v in changes.items():
            before_str = str(v['before'])[:50]
            after_str = str(v['after'])[:50]
            print(f"   • {k}: {before_str} → {after_str}")
        
        return changes


# ---------------------------------------------------------------------------
# Agent Pool (for multi-agent coordination)
# ---------------------------------------------------------------------------

class AgentPool:
    """
    Manages a pool of async agents with message queues.
    
    Usage:
        pool = AgentPool(worker_count=3)
        pool.submit(task)
        results = await pool.gather()
    """

    def __init__(self, worker_count=3):
        self.worker_count = worker_count
        self.task_queue = None
        self.result_queue = None
        self._workers = []

    async def init(self):
        """Initialize async queues."""
        self.task_queue = asyncio.Queue()
        self.result_queue = asyncio.Queue()

    async def submit(self, task):
        """Submit a task to the pool."""
        await self.task_queue.put(task)

    async def submit_batch(self, tasks):
        """Submit multiple tasks."""
        for task in tasks:
            await self.task_queue.put(task)
        # Add sentinel values to signal workers to stop
        for _ in range(self.worker_count):
            await self.task_queue.put(None)

    async def worker(self, worker_id, process_fn):
        """Worker coroutine that processes tasks from the queue."""
        while True:
            task = await self.task_queue.get()
            if task is None:
                break
            
            try:
                result = await process_fn(task)
                await self.result_queue.put({
                    "worker_id": worker_id,
                    "task": task,
                    "result": result,
                    "status": "success"
                })
            except Exception as e:
                await self.result_queue.put({
                    "worker_id": worker_id,
                    "task": task,
                    "error": str(e),
                    "status": "error"
                })

    async def run(self, tasks, process_fn):
        """Run all tasks through the worker pool."""
        await self.init()
        await self.submit_batch(tasks)
        
        # Start workers
        workers = [
            asyncio.create_task(self.worker(i, process_fn))
            for i in range(self.worker_count)
        ]
        
        # Wait for all workers to finish
        await asyncio.gather(*workers)
        
        # Collect results
        results = []
        while not self.result_queue.empty():
            results.append(await self.result_queue.get())
        
        return results


# ---------------------------------------------------------------------------
# Convenience: Quick pipeline builder
# ---------------------------------------------------------------------------

def create_pipeline(nodes, name="Pipeline"):
    """
    Quick helper to create a linear pipeline from a list of nodes.
    
    Usage:
        pipeline = create_pipeline([node_a, node_b, node_c])
        runtime = OrchestratorRuntime(pipeline)
        runtime.run(shared)
    """
    # Import here to avoid circular deps
    try:
        from pocketflow import Flow
    except ImportError:
        # Fallback: create a minimal Flow class
        class Flow:
            def __init__(self, start=None):
                self.start = start
                self.successors = {}
            def run(self, shared):
                node = self.start
                while node:
                    action = node.run(shared)
                    node = node.successors.get(action or "default")
    
    # Chain nodes
    for i in range(len(nodes) - 1):
        nodes[i] >> nodes[i + 1]
    
    return Flow(start=nodes[0])
