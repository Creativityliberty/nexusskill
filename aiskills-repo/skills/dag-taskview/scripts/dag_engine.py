"""
DAG Engine
==========
Builds DAGs from task definitions, detects cycles, computes critical paths,
and renders Mermaid diagrams with progress coloring.

Usage:
    from dag_engine import DAGEngine
    engine = DAGEngine()
    engine.load_yaml("tasks.yaml")
    engine.render("dag.md")
    engine.critical_path()
"""

import json
import yaml
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict, deque

# ---------------------------------------------------------------------------
# Status definitions
# ---------------------------------------------------------------------------

STATUS_CONFIG = {
    "done":        {"emoji": "✅", "color": "#22c55e", "text_color": "#fff", "label": "Done"},
    "in_progress": {"emoji": "🔄", "color": "#eab308", "text_color": "#000", "label": "In Progress"},
    "pending":     {"emoji": "⏳", "color": "#64748b", "text_color": "#fff", "label": "Pending"},
    "blocked":     {"emoji": "🚫", "color": "#ef4444", "text_color": "#fff", "label": "Blocked"},
}


# ---------------------------------------------------------------------------
# DAG Engine
# ---------------------------------------------------------------------------

class DAGEngine:
    """
    Builds and renders DAG-based task trees.
    
    Example:
        engine = DAGEngine()
        engine.add_task("design", "Design API", deps=[])
        engine.add_task("auth", "Build Auth", deps=["design"])
        engine.add_task("crud", "Build CRUD", deps=["design"])
        engine.add_task("tests", "Write Tests", deps=["auth", "crud"])
        engine.add_task("deploy", "Deploy", deps=["tests"])
        
        engine.render("dag_output.md")
        print(engine.critical_path())
        engine.summary()
    """

    def __init__(self, project_name="Project"):
        self.project_name = project_name
        self.tasks = {}       # id -> task dict
        self.task_order = []   # preserve insertion order

    def add_task(self, task_id, name, status="pending", deps=None):
        """Add a task to the DAG."""
        self.tasks[task_id] = {
            "id": task_id,
            "name": name,
            "status": status,
            "deps": deps or []
        }
        if task_id not in self.task_order:
            self.task_order.append(task_id)

    def load_yaml(self, filepath):
        """Load tasks from a YAML file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        self.project_name = data.get("project", "Project")
        for task in data.get("tasks", []):
            self.add_task(
                task_id=task["id"],
                name=task["name"],
                status=task.get("status", "pending"),
                deps=task.get("deps", [])
            )

    def load_dict(self, task_list, project_name="Project"):
        """Load tasks from a list of dicts."""
        self.project_name = project_name
        for task in task_list:
            self.add_task(
                task_id=task["id"],
                name=task["name"],
                status=task.get("status", "pending"),
                deps=task.get("deps", [])
            )

    def validate(self):
        """
        Validate the DAG:
        - Check all deps reference existing tasks
        - Detect cycles
        Returns (is_valid, errors)
        """
        errors = []
        
        # Check deps exist
        for tid, task in self.tasks.items():
            for dep in task["deps"]:
                if dep not in self.tasks:
                    errors.append(f"Task '{tid}' depends on unknown task '{dep}'")
        
        # Cycle detection (Kahn's algorithm)
        in_degree = defaultdict(int)
        adjacency = defaultdict(list)
        
        for tid, task in self.tasks.items():
            if tid not in in_degree:
                in_degree[tid] = 0
            for dep in task["deps"]:
                adjacency[dep].append(tid)
                in_degree[tid] += 1
        
        queue = deque([t for t in self.tasks if in_degree[t] == 0])
        visited = 0
        
        while queue:
            node = queue.popleft()
            visited += 1
            for neighbor in adjacency[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if visited != len(self.tasks):
            errors.append("⚠️ Cycle detected in task dependencies!")
        
        return (len(errors) == 0, errors)

    def topological_sort(self):
        """Return tasks in topological order."""
        in_degree = defaultdict(int)
        adjacency = defaultdict(list)
        
        for tid, task in self.tasks.items():
            if tid not in in_degree:
                in_degree[tid] = 0
            for dep in task["deps"]:
                adjacency[dep].append(tid)
                in_degree[tid] += 1
        
        queue = deque([t for t in self.task_order if in_degree[t] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in adjacency[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result

    def critical_path(self):
        """
        Find the critical path (longest dependency chain).
        Returns list of task IDs on the critical path.
        """
        # Compute longest path to each node
        order = self.topological_sort()
        dist = {tid: 0 for tid in self.tasks}
        parent = {tid: None for tid in self.tasks}
        
        for tid in order:
            for dep in self.tasks[tid]["deps"]:
                if dist[dep] + 1 > dist[tid]:
                    dist[tid] = dist[dep] + 1
                    parent[tid] = dep
        
        # Find end of critical path
        end_node = max(dist, key=dist.get)
        
        # Trace back
        path = []
        current = end_node
        while current is not None:
            path.append(current)
            current = parent[current]
        
        path.reverse()
        return path

    def next_actions(self):
        """Find tasks that can start now (all deps are done)."""
        actionable = []
        for tid, task in self.tasks.items():
            if task["status"] in ("pending", "blocked"):
                all_deps_done = all(
                    self.tasks[dep]["status"] == "done" 
                    for dep in task["deps"] 
                    if dep in self.tasks
                )
                if all_deps_done:
                    actionable.append(tid)
        return actionable

    def blockers(self):
        """Find blocked tasks and what's blocking them."""
        blocked = {}
        for tid, task in self.tasks.items():
            if task["status"] == "blocked" or (
                task["status"] == "pending" and task["deps"]
            ):
                blocking = [
                    dep for dep in task["deps"]
                    if dep in self.tasks and self.tasks[dep]["status"] != "done"
                ]
                if blocking:
                    blocked[tid] = blocking
        return blocked

    def progress(self):
        """Calculate overall progress percentage."""
        if not self.tasks:
            return 0.0
        done = sum(1 for t in self.tasks.values() if t["status"] == "done")
        return round((done / len(self.tasks)) * 100, 1)

    def update_status(self, task_id, new_status):
        """Update a task's status."""
        if task_id not in self.tasks:
            raise ValueError(f"Task '{task_id}' not found")
        if new_status not in STATUS_CONFIG:
            raise ValueError(f"Invalid status '{new_status}'. Use: {list(STATUS_CONFIG.keys())}")
        self.tasks[task_id]["status"] = new_status
        
        # Auto-update blocked tasks: if all deps done, set to pending
        for tid, task in self.tasks.items():
            if task["status"] == "blocked":
                all_deps_done = all(
                    self.tasks[dep]["status"] == "done"
                    for dep in task["deps"]
                    if dep in self.tasks
                )
                if all_deps_done:
                    self.tasks[tid]["status"] = "pending"

    def to_mermaid(self):
        """Generate a Mermaid flowchart diagram."""
        lines = ["flowchart TD"]
        
        cp = set(self.critical_path())
        
        # Define nodes
        for tid in self.task_order:
            task = self.tasks[tid]
            cfg = STATUS_CONFIG.get(task["status"], STATUS_CONFIG["pending"])
            label = f'{cfg["emoji"]} {task["name"]}'
            is_cp = tid in cp
            
            # Use different shapes for critical path
            if is_cp:
                lines.append(f'    {tid}[["<b>{label}</b>"]]:::{task["status"]}')
            else:
                lines.append(f'    {tid}["{label}"]:::{task["status"]}')
        
        lines.append("")
        
        # Define edges
        for tid, task in self.tasks.items():
            for dep in task["deps"]:
                if dep in self.tasks:
                    is_cp_edge = dep in cp and tid in cp
                    if is_cp_edge:
                        lines.append(f"    {dep} ==>|critical| {tid}")
                    else:
                        lines.append(f"    {dep} --> {tid}")
        
        lines.append("")
        
        # Define styles
        for status, cfg in STATUS_CONFIG.items():
            lines.append(f'    classDef {status} fill:{cfg["color"]},color:{cfg["text_color"]},stroke:#333')
        
        return "\n".join(lines)

    def render(self, filepath=None):
        """Render the DAG as a Mermaid diagram in markdown."""
        valid, errors = self.validate()
        
        content_parts = [
            f"# 🌲 DAG: {self.project_name}",
            "",
            f"> Progress: **{self.progress()}%** | "
            f"Tasks: {len(self.tasks)} | "
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
        ]
        
        if not valid:
            content_parts.append("> [!WARNING]")
            for err in errors:
                content_parts.append(f"> {err}")
            content_parts.append("")
        
        # Mermaid diagram
        content_parts.append("```mermaid")
        content_parts.append(self.to_mermaid())
        content_parts.append("```")
        content_parts.append("")
        
        # Legend
        content_parts.append("### Legend")
        content_parts.append("| Status | Color |")
        content_parts.append("|---|---|")
        for status, cfg in STATUS_CONFIG.items():
            content_parts.append(f'| {cfg["emoji"]} {cfg["label"]} | `{cfg["color"]}` |')
        content_parts.append("")
        
        # Critical path
        cp = self.critical_path()
        if cp:
            cp_names = [self.tasks[t]["name"] for t in cp if t in self.tasks]
            content_parts.append(f"### 🔥 Critical Path ({len(cp)} steps)")
            content_parts.append(" → ".join(cp_names))
            content_parts.append("")
        
        # Next actions
        actions = self.next_actions()
        if actions:
            content_parts.append("### ▶️ Ready to Start")
            for a in actions:
                content_parts.append(f"- {self.tasks[a]['name']}")
            content_parts.append("")
        
        # Blockers
        blocked = self.blockers()
        if blocked:
            content_parts.append("### 🚫 Blocked")
            for tid, blocking in blocked.items():
                blocking_names = [self.tasks[b]["name"] for b in blocking if b in self.tasks]
                content_parts.append(f"- **{self.tasks[tid]['name']}** ← waiting for: {', '.join(blocking_names)}")
            content_parts.append("")
        
        content = "\n".join(content_parts)
        
        if filepath:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"🌲 DAG rendered to {path}")
        
        return content

    def summary(self):
        """Print a human-readable summary."""
        print(f"\n{'=' * 50}")
        print(f"  DAG: {self.project_name}")
        print(f"{'=' * 50}")
        print(f"  Tasks:    {len(self.tasks)}")
        print(f"  Progress: {self.progress()}%")
        
        by_status = defaultdict(int)
        for task in self.tasks.values():
            by_status[task["status"]] += 1
        
        for status, count in by_status.items():
            cfg = STATUS_CONFIG.get(status, {})
            print(f"    {cfg.get('emoji', '?')} {status}: {count}")
        
        cp = self.critical_path()
        cp_names = [self.tasks[t]["name"] for t in cp if t in self.tasks]
        print(f"\n  Critical Path: {' → '.join(cp_names)}")
        
        actions = self.next_actions()
        if actions:
            print(f"\n  Ready to start:")
            for a in actions:
                print(f"    → {self.tasks[a]['name']}")
        
        print(f"{'=' * 50}\n")

    def export_yaml(self, filepath):
        """Export current DAG state to YAML."""
        data = {
            "project": self.project_name,
            "tasks": [self.tasks[tid] for tid in self.task_order]
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        print(f"📄 DAG exported to {filepath}")

    def export_json(self, filepath):
        """Export current DAG state to JSON."""
        data = {
            "project": self.project_name,
            "tasks": [self.tasks[tid] for tid in self.task_order],
            "progress": self.progress(),
            "critical_path": self.critical_path(),
            "next_actions": self.next_actions()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"📄 DAG exported to {filepath}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="DAG TaskView — Visual Task Tree")
    parser.add_argument("--input", required=True, help="YAML task file")
    parser.add_argument("--output", default="dag.md", help="Output markdown file")
    parser.add_argument("--format", default="mermaid", choices=["mermaid", "json", "yaml"])
    
    args = parser.parse_args()
    
    engine = DAGEngine()
    engine.load_yaml(args.input)
    
    valid, errors = engine.validate()
    if not valid:
        print("⚠️ DAG validation errors:")
        for e in errors:
            print(f"  - {e}")
    
    if args.format == "mermaid":
        engine.render(args.output)
    elif args.format == "json":
        engine.export_json(args.output)
    elif args.format == "yaml":
        engine.export_yaml(args.output)
    
    engine.summary()


if __name__ == "__main__":
    main()
