"""
Multi-Agent Pipeline Template
===============================
A ready-to-use template: Planner → Worker Pool → Reviewer → Finalize.

Usage:
    python multi_agent_pipeline.py
"""

import sys
import os
import json

# Add parent for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

# ---------------------------------------------------------------------------
# Minimal PocketFlow primitives (standalone, no external dependency needed)
# ---------------------------------------------------------------------------

class Node:
    """Minimal PocketFlow Node: prep → exec → post."""
    def __init__(self, max_retries=1, wait=0):
        self.max_retries = max_retries
        self.wait = wait
        self.cur_retry = 0
        self.successors = {}
        self.params = {}
    
    def set_params(self, params):
        self.params = params
    
    def prep(self, shared):
        return None
    
    def exec(self, prep_res):
        return None
    
    def post(self, shared, prep_res, exec_res):
        return None
    
    def exec_fallback(self, prep_res, exc):
        raise exc
    
    def run(self, shared):
        prep_res = self.prep(shared)
        exec_res = None
        for i in range(self.max_retries):
            self.cur_retry = i
            try:
                exec_res = self.exec(prep_res)
                break
            except Exception as e:
                if i == self.max_retries - 1:
                    exec_res = self.exec_fallback(prep_res, e)
        action = self.post(shared, prep_res, exec_res)
        return action
    
    def __rshift__(self, other):
        self.successors["default"] = other
        return other
    
    def __sub__(self, action):
        return _ActionConnector(self, action)


class _ActionConnector:
    def __init__(self, node, action):
        self.node = node
        self.action = action
    def __rshift__(self, other):
        self.node.successors[self.action] = other
        return other


class BatchNode(Node):
    """Node that processes items in batch."""
    def run(self, shared):
        prep_res = self.prep(shared)
        exec_results = []
        for item in (prep_res or []):
            for i in range(self.max_retries):
                self.cur_retry = i
                try:
                    result = self.exec(item)
                    exec_results.append(result)
                    break
                except Exception as e:
                    if i == self.max_retries - 1:
                        exec_results.append(self.exec_fallback(item, e))
        action = self.post(shared, prep_res, exec_results)
        return action


class Flow(Node):
    """Orchestrates a directed graph of Nodes."""
    def __init__(self, start=None):
        super().__init__()
        self.start = start
    
    def run(self, shared):
        prep_res = self.prep(shared)
        current = self.start
        while current:
            # Propagate params
            if hasattr(current, 'set_params'):
                merged = {**self.params, **current.params}
                current.set_params(merged)
            
            action = current.run(shared)
            action = action or "default"
            current = current.successors.get(action)
        
        result = self.post(shared, prep_res, None)
        return result


# ---------------------------------------------------------------------------
# Pipeline Agents
# ---------------------------------------------------------------------------

class PlannerAgent(Node):
    """Decomposes a complex task into subtasks."""
    
    def prep(self, shared):
        return shared.get("task_description", "No task specified")
    
    def exec(self, task):
        # In production, replace with call_llm()
        print(f"\n🧠 [Planner] Analyzing task: {task[:60]}...")
        
        # Simulate LLM decomposition
        subtasks = [
            {"id": 1, "description": f"Research and plan: {task[:30]}...", "priority": "high"},
            {"id": 2, "description": f"Implement core logic for: {task[:30]}...", "priority": "high"},
            {"id": 3, "description": f"Write tests for: {task[:30]}...", "priority": "medium"},
            {"id": 4, "description": f"Document: {task[:30]}...", "priority": "low"},
        ]
        return subtasks
    
    def post(self, shared, prep_res, exec_res):
        shared["subtasks"] = exec_res
        shared["completed_tasks"] = []
        print(f"   → Decomposed into {len(exec_res)} subtasks")
        return "dispatch"


class WorkerPool(BatchNode):
    """Processes subtasks in parallel (batch)."""
    
    def prep(self, shared):
        return shared.get("subtasks", [])
    
    def exec(self, subtask):
        # In production, replace with call_llm() per subtask
        print(f"   ⚙️  [Worker] Processing: {subtask['description'][:50]}...")
        
        # Simulate work
        result = {
            "subtask_id": subtask["id"],
            "status": "completed",
            "output": f"Completed: {subtask['description']}",
            "quality_score": 0.85
        }
        return result
    
    def post(self, shared, prep_res, exec_res_list):
        shared["worker_results"] = exec_res_list
        print(f"   → {len(exec_res_list)} subtasks completed")
        return "review"


class ReviewerAgent(Node):
    """Reviews all worker outputs and decides if quality is sufficient."""
    
    def prep(self, shared):
        return shared.get("worker_results", [])
    
    def exec(self, results):
        # In production, replace with call_llm()
        print(f"\n🔍 [Reviewer] Reviewing {len(results)} results...")
        
        # Check quality scores
        avg_quality = sum(r.get("quality_score", 0) for r in results) / max(len(results), 1)
        
        review = {
            "approved": avg_quality >= 0.7,
            "avg_quality": round(avg_quality, 2),
            "feedback": "Quality meets threshold" if avg_quality >= 0.7 else "Quality below threshold, retry needed",
            "details": [
                {"subtask_id": r["subtask_id"], "quality": r.get("quality_score", 0)}
                for r in results
            ]
        }
        return review
    
    def post(self, shared, prep_res, exec_res):
        shared["review"] = exec_res
        retry_count = shared.get("retry_count", 0)
        
        if exec_res["approved"]:
            print(f"   ✅ Approved (avg quality: {exec_res['avg_quality']})")
            return "approved"
        elif retry_count < 2:
            shared["retry_count"] = retry_count + 1
            print(f"   🔄 Retry #{retry_count + 1} (avg quality: {exec_res['avg_quality']})")
            return "retry"
        else:
            print(f"   ⚠️  Max retries reached, approving with lower quality")
            return "approved"


class FinalizeNode(Node):
    """Produces the final output."""
    
    def prep(self, shared):
        return shared.get("worker_results", []), shared.get("review", {})
    
    def exec(self, inputs):
        results, review = inputs
        # In production, replace with call_llm() to synthesize
        print(f"\n📦 [Finalizer] Assembling final output...")
        
        final = {
            "summary": f"Pipeline completed with {len(results)} subtasks",
            "quality": review.get("avg_quality", "N/A"),
            "outputs": [r.get("output", "") for r in results]
        }
        return final
    
    def post(self, shared, prep_res, exec_res):
        shared["final_output"] = exec_res
        print(f"   ✅ Final output ready!")
        return None  # End of pipeline


# ---------------------------------------------------------------------------
# Build and run the pipeline
# ---------------------------------------------------------------------------

def build_pipeline():
    """Build the Planner → Workers → Reviewer → Finalize pipeline."""
    planner = PlannerAgent()
    workers = WorkerPool()
    reviewer = ReviewerAgent()
    finalizer = FinalizeNode()
    
    # Wire the flow
    planner - "dispatch" >> workers
    workers - "review" >> reviewer
    reviewer - "approved" >> finalizer
    reviewer - "retry" >> planner  # Loop back if quality is low
    
    return Flow(start=planner)


def main():
    """Run the multi-agent pipeline with orchestrator."""
    from orchestrator import OrchestratorRuntime
    
    # Build pipeline
    pipeline = build_pipeline()
    
    # Wrap with orchestrator
    runtime = OrchestratorRuntime(
        pipeline,
        enable_trace=True,
        enable_snapshots=True,
        snapshot_dir=".pipeline_snapshots"
    )
    
    # Define the task
    shared = {
        "task_description": "Build a REST API for user management with authentication, CRUD endpoints, and rate limiting"
    }
    
    print("=" * 60)
    print("  MULTI-AGENT PIPELINE — Flow Orchestrator")
    print("=" * 60)
    
    # Run the pipeline
    runtime.run(shared)
    
    # Print results
    print("\n" + "=" * 60)
    print("  RESULTS")
    print("=" * 60)
    print(json.dumps(shared.get("final_output", {}), indent=2))
    
    # Export trace
    runtime.tracer.summary()
    runtime.tracer.export("trace_output.json")
    runtime.tracer.to_mermaid("trace_diagram.md")
    
    # Show runtime status
    print("\n📊 Runtime Status:")
    print(json.dumps(runtime.status(), indent=2, default=str))


if __name__ == "__main__":
    main()
