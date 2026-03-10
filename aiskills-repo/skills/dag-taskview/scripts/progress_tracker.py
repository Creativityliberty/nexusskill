"""
Progress Tracker
=================
High-level wrapper for DAG task tracking with persistent state.

Usage:
    from progress_tracker import ProgressTracker
    
    tracker = ProgressTracker("tasks.yaml")
    tracker.update("auth", "done")
    tracker.update("api", "in_progress")
    tracker.render("dag.md")
    tracker.summary()
"""

import yaml
from pathlib import Path
from dag_engine import DAGEngine


class ProgressTracker:
    """
    Persistent progress tracker backed by a YAML file.
    Updates task statuses and regenerates DAG visualizations.
    """

    def __init__(self, yaml_path):
        self.yaml_path = Path(yaml_path)
        self.engine = DAGEngine()
        
        if self.yaml_path.exists():
            self.engine.load_yaml(str(self.yaml_path))
        else:
            print(f"📝 Creating new task file: {self.yaml_path}")

    def update(self, task_id, status):
        """Update a task status and persist."""
        self.engine.update_status(task_id, status)
        self._save()
        
        cfg_emoji = {"done": "✅", "in_progress": "🔄", "pending": "⏳", "blocked": "🚫"}
        emoji = cfg_emoji.get(status, "?")
        task_name = self.engine.tasks[task_id]["name"]
        print(f"  {emoji} {task_name} → {status}")

    def batch_update(self, updates):
        """Update multiple tasks at once. updates = [(task_id, status), ...]"""
        for task_id, status in updates:
            self.engine.update_status(task_id, status)
        self._save()
        print(f"  📦 Updated {len(updates)} tasks")

    def add_task(self, task_id, name, deps=None, status="pending"):
        """Add a new task."""
        self.engine.add_task(task_id, name, status=status, deps=deps)
        self._save()
        print(f"  ➕ Added: {name}")

    def remove_task(self, task_id):
        """Remove a task (and clean up deps)."""
        if task_id in self.engine.tasks:
            name = self.engine.tasks[task_id]["name"]
            del self.engine.tasks[task_id]
            self.engine.task_order.remove(task_id)
            
            # Clean deps in other tasks
            for tid, task in self.engine.tasks.items():
                if task_id in task["deps"]:
                    task["deps"].remove(task_id)
            
            self._save()
            print(f"  ➖ Removed: {name}")

    def render(self, filepath="dag.md"):
        """Render the current DAG to a file."""
        return self.engine.render(filepath)

    def summary(self):
        """Print progress summary."""
        self.engine.summary()

    def progress(self):
        """Get progress percentage."""
        return self.engine.progress()

    def what_next(self):
        """Show actionable tasks."""
        actions = self.engine.next_actions()
        if actions:
            print("\n▶️  Ready to start:")
            for a in actions:
                print(f"   → {self.engine.tasks[a]['name']}")
        else:
            in_progress = [t for t in self.engine.tasks.values() if t["status"] == "in_progress"]
            if in_progress:
                print("\n🔄 Currently in progress:")
                for t in in_progress:
                    print(f"   → {t['name']}")
            else:
                done_count = sum(1 for t in self.engine.tasks.values() if t["status"] == "done")
                if done_count == len(self.engine.tasks):
                    print("\n🎉 All tasks completed!")
                else:
                    print("\n🚫 All remaining tasks are blocked")
        return actions

    def _save(self):
        """Persist current state to YAML."""
        data = {
            "project": self.engine.project_name,
            "tasks": [self.engine.tasks[tid] for tid in self.engine.task_order]
        }
        with open(self.yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

def demo():
    """Run a quick demo of the progress tracker."""
    print("=" * 50)
    print("  PROGRESS TRACKER DEMO")
    print("=" * 50)
    
    # Create a sample project
    tracker = ProgressTracker("demo_tasks.yaml")
    
    tracker.add_task("design", "Design Architecture", deps=[])
    tracker.add_task("auth", "Implement Auth", deps=["design"])
    tracker.add_task("crud", "Build CRUD API", deps=["design"])
    tracker.add_task("tests", "Write Tests", deps=["auth", "crud"])
    tracker.add_task("deploy", "Deploy to Production", deps=["tests"])
    
    print(f"\n📊 Initial state:")
    tracker.summary()
    tracker.render("demo_dag_1.md")
    
    # Simulate progress
    print("\n--- Simulating progress ---\n")
    tracker.update("design", "done")
    tracker.update("auth", "in_progress")
    
    tracker.what_next()
    tracker.render("demo_dag_2.md")
    
    # More progress
    tracker.update("auth", "done")
    tracker.update("crud", "in_progress")
    
    print(f"\n📊 After more progress:")
    tracker.summary()
    tracker.render("demo_dag_3.md")
    
    # Clean up
    import os
    for f in ["demo_tasks.yaml", "demo_dag_1.md", "demo_dag_2.md", "demo_dag_3.md"]:
        if os.path.exists(f):
            os.remove(f)
    
    print("✅ Demo complete!")


if __name__ == "__main__":
    demo()
