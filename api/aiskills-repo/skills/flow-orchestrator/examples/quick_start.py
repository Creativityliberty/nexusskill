"""
Quick Start Example
====================
Demonstrates the simplest possible usage of the Flow Orchestrator.

Run:
    python quick_start.py
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'templates'))

from multi_agent_pipeline import Node, Flow, build_pipeline
from orchestrator import OrchestratorRuntime, SnapshotManager


def example_basic():
    """Basic: Run a simple 2-node pipeline with tracing."""
    print("\n📌 Example 1: Basic Pipeline with Tracing\n")
    
    class Greet(Node):
        def exec(self, _):
            return "Hello from Node!"
        def post(self, shared, prep_res, exec_res):
            shared["greeting"] = exec_res
            print(f"   Greet: {exec_res}")
    
    class Respond(Node):
        def prep(self, shared):
            return shared.get("greeting", "")
        def exec(self, greeting):
            return f"Response to: {greeting}"
        def post(self, shared, prep_res, exec_res):
            shared["response"] = exec_res
            print(f"   Respond: {exec_res}")
    
    greet = Greet()
    respond = Respond()
    greet >> respond
    
    flow = Flow(start=greet)
    runtime = OrchestratorRuntime(flow, enable_trace=True, enable_snapshots=False)
    
    shared = {}
    runtime.run(shared)
    runtime.tracer.summary()


def example_snapshots():
    """Snapshots: Save and restore state."""
    print("\n📌 Example 2: Snapshots\n")
    
    sm = SnapshotManager(".example_snapshots")
    
    # Save state
    shared = {"counter": 0, "results": ["item1", "item2"]}
    sm.save(shared, "checkpoint_a")
    
    # Modify state
    shared["counter"] = 42
    shared["results"].append("item3")
    sm.save(shared, "checkpoint_b")
    
    # Show diff
    sm.diff("checkpoint_a", "checkpoint_b")
    
    # Restore
    restored = sm.load("checkpoint_a")
    print(f"   Restored counter: {restored['counter']} (should be 0)")
    
    # Cleanup
    import shutil
    shutil.rmtree(".example_snapshots", ignore_errors=True)


def example_full_pipeline():
    """Full Pipeline: Run the multi-agent template."""
    print("\n📌 Example 3: Full Multi-Agent Pipeline\n")
    
    pipeline = build_pipeline()
    runtime = OrchestratorRuntime(pipeline, enable_trace=True, enable_snapshots=True,
                                  snapshot_dir=".example_pipeline_snapshots")
    
    shared = {
        "task_description": "Create a markdown-to-HTML converter with syntax highlighting"
    }
    
    runtime.run(shared)
    runtime.tracer.summary()
    
    # Cleanup
    import shutil
    shutil.rmtree(".example_pipeline_snapshots", ignore_errors=True)


if __name__ == "__main__":
    print("=" * 60)
    print("  FLOW ORCHESTRATOR — Quick Start Examples")
    print("=" * 60)
    
    example_basic()
    example_snapshots()
    example_full_pipeline()
    
    print("\n✅ All examples completed!")
