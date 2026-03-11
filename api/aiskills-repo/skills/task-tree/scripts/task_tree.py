#!/usr/bin/env python3
"""
Task Tree — DAG Generator, Validator & Renderer
================================================
Decomposes goals into directed acyclic graphs of tasks.

Commands:
  generate   Interactive goal → task-tree.yaml
  validate   Check for cycles + schema errors
  render     Print ASCII tree + critical path
  critical   Show the critical path (longest dependency chain)

Usage:
  python task_tree.py generate --goal "Build a fintech MVP" --output task-tree.yaml
  python task_tree.py validate --file task-tree.yaml
  python task_tree.py render --file task-tree.yaml
  python task_tree.py critical --file task-tree.yaml
"""

from __future__ import annotations
import argparse
import json
import sys
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

REQUIRED_TASK_FIELDS = {"id", "name", "description", "depends_on"}
KNOWN_SKILLS = [
    "ui-style-generator", "commit", "review-pr", "skill-creator",
    "pocketflow", "session-start-hook", "keybindings-help",
    "num-agents", "skill-architect", "task-tree",
    "morsel-tasks", "artifacts-maker", "workflow",
]


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_tree(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    if HAS_YAML:
        return yaml.safe_load(content)
    # Fallback: try JSON
    return json.loads(content)


def save_tree(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if HAS_YAML:
        path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    else:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_tree(data: dict) -> list[str]:
    errors: list[str] = []

    if "goal" not in data:
        errors.append("Missing 'goal' field")
    if "tasks" not in data or not isinstance(data["tasks"], list):
        errors.append("Missing or invalid 'tasks' list")
        return errors

    tasks = data["tasks"]
    task_ids = {t.get("id") for t in tasks if "id" in t}

    for i, task in enumerate(tasks):
        prefix = f"Task[{i}]"

        for field in REQUIRED_TASK_FIELDS:
            if field not in task:
                errors.append(f"{prefix} missing required field: '{field}'")

        task_id = task.get("id", f"?{i}")

        # Check skill is known (warn, not error)
        skill = task.get("skill")
        if skill and skill not in KNOWN_SKILLS:
            errors.append(f"Task '{task_id}': unknown skill '{skill}' (add to KNOWN_SKILLS)")

        # Check depends_on references
        for dep in task.get("depends_on", []):
            if dep not in task_ids:
                errors.append(f"Task '{task_id}' depends on unknown task '{dep}'")

    # Cycle detection (Kahn's algorithm)
    graph: dict[str, list[str]] = defaultdict(list)
    in_degree: dict[str, int] = {t["id"]: 0 for t in tasks if "id" in t}

    for task in tasks:
        tid = task.get("id")
        if not tid:
            continue
        for dep in task.get("depends_on", []):
            if dep in in_degree:
                graph[dep].append(tid)
                in_degree[tid] = in_degree.get(tid, 0) + 1

    queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if visited != len(in_degree):
        errors.append("Cycle detected in task dependencies! DAG is invalid.")

    return errors


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def compute_levels(tasks: list[dict]) -> dict[str, int]:
    """Assign topological levels for rendering."""
    levels: dict[str, int] = {}
    task_map = {t["id"]: t for t in tasks if "id" in t}

    def get_level(tid: str, visited: set[str]) -> int:
        if tid in levels:
            return levels[tid]
        if tid in visited:
            return 0  # cycle guard
        visited.add(tid)
        deps = task_map.get(tid, {}).get("depends_on", [])
        if not deps:
            levels[tid] = 0
        else:
            levels[tid] = 1 + max(get_level(d, visited) for d in deps)
        return levels[tid]

    for t in tasks:
        get_level(t["id"], set())
    return levels


def render_tree(data: dict) -> str:
    tasks = data.get("tasks", [])
    goal = data.get("goal", "Unknown goal")
    levels = compute_levels(tasks)

    # Group by level
    by_level: dict[int, list[dict]] = defaultdict(list)
    for t in tasks:
        by_level[levels.get(t.get("id", ""), 0)].append(t)

    lines = [f"Goal: {goal}", "│"]
    max_level = max(by_level.keys()) if by_level else 0

    for level in range(max_level + 1):
        level_tasks = by_level[level]
        for i, task in enumerate(level_tasks):
            tid = task.get("id", "?")
            name = task.get("name", "?")
            skill = task.get("skill", "direct")
            skill_label = f"({skill})" if skill else "(direct)"
            is_last = (i == len(level_tasks) - 1) and (level == max_level)
            prefix = "└── " if is_last else "├── "
            parallel = task.get("parallel_with", [])
            parallel_note = f" ──┐ parallel with {parallel}" if parallel else ""
            lines.append(f"{prefix}[{tid}] {name} {skill_label}{parallel_note}")

            deps = task.get("depends_on", [])
            if deps:
                lines.append(f"│        depends on: {', '.join(deps)}")
        if level < max_level:
            lines.append("│")

    return "\n".join(lines)


def critical_path(data: dict) -> list[str]:
    """Find the longest dependency chain (critical path)."""
    tasks = data.get("tasks", [])
    task_map = {t["id"]: t for t in tasks if "id" in t}
    morsels = {t["id"]: t.get("estimated_morsels", 1) for t in tasks if "id" in t}

    dist: dict[str, int] = {}
    prev: dict[str, str | None] = {}

    def longest(tid: str, visited: set[str]) -> int:
        if tid in dist:
            return dist[tid]
        if tid in visited:
            return 0
        visited.add(tid)
        deps = task_map.get(tid, {}).get("depends_on", [])
        if not deps:
            dist[tid] = morsels.get(tid, 1)
            prev[tid] = None
        else:
            best_dep = max(deps, key=lambda d: longest(d, set(visited)))
            dist[tid] = longest(best_dep, set(visited)) + morsels.get(tid, 1)
            prev[tid] = best_dep
        return dist[tid]

    for t in tasks:
        longest(t["id"], set())

    if not dist:
        return []

    # Trace back from endpoint with max distance
    end = max(dist, key=lambda k: dist[k])
    path: list[str] = []
    cur: str | None = end
    while cur:
        path.insert(0, cur)
        cur = prev.get(cur)
    return path


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_validate(path: Path) -> None:
    data = load_tree(path)
    errors = validate_tree(data)
    if errors:
        print(f"❌ Validation failed ({len(errors)} errors):")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)
    else:
        tasks = data.get("tasks", [])
        print(f"✅ Valid DAG: {len(tasks)} tasks, no cycles")


def cmd_render(path: Path) -> None:
    data = load_tree(path)
    errors = validate_tree(data)
    if errors:
        print(f"⚠️  {len(errors)} validation warning(s)")
    print("\n" + render_tree(data) + "\n")

    # Stats
    tasks = data.get("tasks", [])
    total_morsels = sum(t.get("estimated_morsels", 1) for t in tasks)
    parallel_tasks = [t["id"] for t in tasks if t.get("parallel_with")]
    cp = critical_path(data)
    cp_morsels = sum(
        next((t.get("estimated_morsels", 1) for t in tasks if t["id"] == tid), 1)
        for tid in cp
    )

    print(f"Stats:")
    print(f"  Tasks:            {len(tasks)}")
    print(f"  Total morsels:    {total_morsels}")
    print(f"  Parallelizable:   {len(parallel_tasks)} tasks")
    print(f"  Critical path:    {' → '.join(cp)} ({cp_morsels} morsels)")


def cmd_critical(path: Path) -> None:
    data = load_tree(path)
    cp = critical_path(data)
    tasks = data.get("tasks", [])
    task_map = {t["id"]: t for t in tasks if "id" in t}
    print(f"\nCritical path ({len(cp)} tasks):")
    for tid in cp:
        t = task_map.get(tid, {})
        m = t.get("estimated_morsels", 1)
        print(f"  [{tid}] {t.get('name', '?')} — {m} morsel(s)")


def cmd_generate(goal: str, output: Path) -> None:
    """Scaffold a task-tree.yaml template for the given goal."""
    now = datetime.now(timezone.utc).isoformat()
    template: dict[str, Any] = {
        "goal": goal,
        "version": "1.0",
        "created_at": now,
        "tasks": [
            {
                "id": "t1",
                "name": "TODO: first task name",
                "description": "TODO: describe what this task does",
                "skill": "TODO: skill-name or null",
                "input": {},
                "output_artifact": "output.md",
                "artifact_type": "markdown",
                "depends_on": [],
                "parallel_with": [],
                "estimated_morsels": 1,
            },
            {
                "id": "t2",
                "name": "TODO: second task name",
                "description": "TODO: describe what this task does",
                "skill": None,
                "input": {},
                "output_artifact": "output2.txt",
                "artifact_type": "text",
                "depends_on": ["t1"],
                "parallel_with": [],
                "estimated_morsels": 1,
            },
        ],
    }
    save_tree(template, output)
    print(f"✅ Template generated: {output}")
    print("Edit the TODO fields, then run: task_tree.py validate --file", output)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Task Tree — DAG generator & validator")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Scaffold a task-tree.yaml template")
    p_gen.add_argument("--goal", required=True)
    p_gen.add_argument("--output", type=Path, default=Path("task-tree.yaml"))

    p_val = sub.add_parser("validate", help="Validate a task-tree.yaml")
    p_val.add_argument("--file", type=Path, required=True)

    p_ren = sub.add_parser("render", help="Print ASCII tree + stats")
    p_ren.add_argument("--file", type=Path, required=True)

    p_crit = sub.add_parser("critical", help="Show the critical path")
    p_crit.add_argument("--file", type=Path, required=True)

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args.goal, args.output)
    elif args.command == "validate":
        cmd_validate(args.file)
    elif args.command == "render":
        cmd_render(args.file)
    elif args.command == "critical":
        cmd_critical(args.file)


if __name__ == "__main__":
    main()
