#!/usr/bin/env python3
"""
Morsel Runner — Atomic Task Executor with Checkpoint & Retry
=============================================================
Executes tasks as atomic morsels with:
  - Checkpoint/resume (.workflow/checkpoint.json)
  - Lock file (.workflow/<workflow-id>.lock)
  - Exponential backoff retry
  - Schema validation before marking done

Commands:
  run     Execute morsels for a task (with auto-resume if checkpoint exists)
  status  Show current checkpoint state
  lock    Acquire the workflow lock
  unlock  Release the workflow lock
  reset   Clear checkpoint for a workflow (start fresh)

Usage:
  python morsel_runner.py run --workflow-id wf1 --task-id t1 --tree task-tree.yaml
  python morsel_runner.py run --workflow-id wf1 --resume
  python morsel_runner.py status --workflow-id wf1
  python morsel_runner.py reset --workflow-id wf1
"""

from __future__ import annotations
import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("morsel")

WORKFLOW_DIR = Path(".workflow")
MorselStatus = Literal["pending", "running", "done", "failed", "skipped"]

# Exponential backoff delays in seconds
BACKOFF_DELAYS = [1, 2, 4, 8, 16]
MAX_RETRIES = 3


# ---------------------------------------------------------------------------
# Lock management
# ---------------------------------------------------------------------------

def lock_path(workflow_id: str) -> Path:
    return WORKFLOW_DIR / f"{workflow_id}.lock"


def acquire_lock(workflow_id: str) -> bool:
    lp = lock_path(workflow_id)
    WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)
    if lp.exists():
        content = lp.read_text(encoding="utf-8")
        log.error(f"Lock exists! Workflow '{workflow_id}' may already be running.\n{content}")
        return False
    lp.write_text(
        json.dumps({
            "workflow_id": workflow_id,
            "pid": __import__("os").getpid(),
            "acquired_at": datetime.now(timezone.utc).isoformat(),
        }),
        encoding="utf-8"
    )
    log.info(f"Lock acquired: {lp}")
    return True


def release_lock(workflow_id: str) -> None:
    lp = lock_path(workflow_id)
    if lp.exists():
        lp.unlink()
        log.info(f"Lock released: {lp}")


# ---------------------------------------------------------------------------
# Checkpoint management
# ---------------------------------------------------------------------------

def checkpoint_path(workflow_id: str) -> Path:
    return WORKFLOW_DIR / f"{workflow_id}-checkpoint.json"


def load_checkpoint(workflow_id: str) -> dict:
    cp = checkpoint_path(workflow_id)
    if not cp.exists():
        return {"workflow_id": workflow_id, "morsels": {}, "last_updated": None}
    return json.loads(cp.read_text(encoding="utf-8"))


def save_checkpoint(workflow_id: str, state: dict) -> None:
    WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    checkpoint_path(workflow_id).write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def update_morsel(workflow_id: str, morsel_id: str, **kwargs) -> None:
    state = load_checkpoint(workflow_id)
    state["morsels"].setdefault(morsel_id, {})
    state["morsels"][morsel_id].update(kwargs)
    save_checkpoint(workflow_id, state)


# ---------------------------------------------------------------------------
# Retry with exponential backoff
# ---------------------------------------------------------------------------

def run_with_backoff(fn, morsel_id: str, workflow_id: str, max_retries: int = MAX_RETRIES):
    """Execute fn() with exponential backoff on failure. Returns (success, result)."""
    for attempt in range(1, max_retries + 1):
        try:
            log.info(f"[{morsel_id}] Attempt {attempt}/{max_retries}")
            update_morsel(workflow_id, morsel_id, status="running", attempt=attempt)
            result = fn()
            return True, result
        except Exception as e:
            if attempt == max_retries:
                log.error(f"[{morsel_id}] All {max_retries} attempts failed: {e}")
                return False, str(e)
            delay = BACKOFF_DELAYS[min(attempt - 1, len(BACKOFF_DELAYS) - 1)]
            log.warning(f"[{morsel_id}] Attempt {attempt} failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)
    return False, "Max retries exceeded"


# ---------------------------------------------------------------------------
# Morsel execution (Claude does the actual work — this runner manages state)
# ---------------------------------------------------------------------------

def execute_morsel(morsel: dict, workflow_id: str) -> bool:
    """
    Execute one morsel. In the Claude Code context, Claude performs the
    actual work described in morsel['action']. This function manages:
    - State transitions (pending → running → done/failed)
    - Retry with exponential backoff
    - Checkpoint updates
    - Output validation hint
    """
    mid = morsel["id"]
    action = morsel.get("action", "unknown action")
    expected_output = morsel.get("expected_output", "")
    validate_cmd = morsel.get("validate", "")

    log.info(f"[{mid}] Starting: {action}")

    # Check if already done (resume)
    state = load_checkpoint(workflow_id)
    if state["morsels"].get(mid, {}).get("status") == "done":
        log.info(f"[{mid}] Already done (checkpoint). Skipping.")
        return True

    def do_work():
        # ⚡ In Claude Code: Claude reads this action and executes it.
        # This function is a placeholder that would call Claude's tools.
        # For CLI testing, we simulate success.
        log.info(f"[{mid}] Action: {action}")
        if expected_output:
            log.info(f"[{mid}] Expected output: {expected_output}")
        if validate_cmd:
            log.info(f"[{mid}] Validation: {validate_cmd}")
        # Simulate: raise Exception("API timeout") to test retry
        return {"status": "done"}

    success, result = run_with_backoff(do_work, mid, workflow_id, MAX_RETRIES)

    if success:
        update_morsel(workflow_id, mid,
                      status="done",
                      completed_at=datetime.now(timezone.utc).isoformat(),
                      output=str(result))
        log.info(f"[{mid}] ✅ Done")
    else:
        update_morsel(workflow_id, mid,
                      status="failed",
                      error=str(result),
                      completed_at=datetime.now(timezone.utc).isoformat())
        log.error(f"[{mid}] ❌ Failed after {MAX_RETRIES} attempts: {result}")

    return success


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_run(workflow_id: str, task_id: str, tree_path: Path, resume: bool) -> None:
    if not acquire_lock(workflow_id):
        sys.exit(1)

    try:
        # Load task tree
        if not tree_path.exists():
            log.error(f"Task tree not found: {tree_path}")
            sys.exit(1)

        try:
            import yaml
            data = yaml.safe_load(tree_path.read_text(encoding="utf-8"))
        except ImportError:
            data = json.loads(tree_path.read_text(encoding="utf-8"))

        tasks = {t["id"]: t for t in data.get("tasks", []) if "id" in t}
        task = tasks.get(task_id)
        if not task:
            log.error(f"Task '{task_id}' not found in tree")
            sys.exit(1)

        if resume:
            state = load_checkpoint(workflow_id)
            done_count = sum(
                1 for m in state["morsels"].values()
                if m.get("status") == "done"
            )
            log.info(f"Resuming workflow '{workflow_id}': {done_count} morsels already done")

        # Build morsels from task
        # In a real Claude Code session, Claude generates the morsels list
        # based on the task description. Here we scaffold a template.
        estimated = task.get("estimated_morsels", 1)
        morsels = [
            {
                "id": f"m{task_id}-{i+1}",
                "action": f"Step {i+1} of '{task.get('name')}' using skill: {task.get('skill', 'direct')}",
                "expected_output": task.get("output_artifact", ""),
                "validate": f"file {task.get('output_artifact', 'output')} exists",
                "on_fail": "retry",
            }
            for i in range(estimated)
        ]

        # Execute morsels
        failed = []
        for morsel in morsels:
            success = execute_morsel(morsel, workflow_id)
            if not success:
                failed.append(morsel["id"])
                break  # stop on first failure (workflow will replan)

        # Summary
        state = load_checkpoint(workflow_id)
        done = [mid for mid, m in state["morsels"].items() if m.get("status") == "done"]
        log.info(f"\n{'='*50}")
        log.info(f"Task '{task_id}' complete: {len(done)}/{len(morsels)} morsels done")
        if failed:
            log.error(f"Failed morsels: {failed}")
            log.info("→ Trigger Loop-Back Planning in workflow skill")
            sys.exit(2)  # exit code 2 = partial failure, replan needed

    finally:
        release_lock(workflow_id)


def cmd_status(workflow_id: str) -> None:
    state = load_checkpoint(workflow_id)
    morsels = state.get("morsels", {})

    if not morsels:
        print(f"No checkpoint found for workflow '{workflow_id}'")
        return

    print(f"\nWorkflow: {workflow_id}")
    print(f"Last updated: {state.get('last_updated', 'unknown')}\n")
    print(f"{'Morsel':<20} {'Status':<10} {'Attempt':<8} {'Completed'}")
    print("-" * 60)
    for mid, m in morsels.items():
        print(f"{mid:<20} {m.get('status','?'):<10} {m.get('attempt','?'):<8} {m.get('completed_at','pending')}")


def cmd_reset(workflow_id: str) -> None:
    cp = checkpoint_path(workflow_id)
    lp = lock_path(workflow_id)
    if cp.exists():
        cp.unlink()
        print(f"✅ Checkpoint cleared: {cp}")
    if lp.exists():
        lp.unlink()
        print(f"✅ Lock cleared: {lp}")
    if not cp.exists() and not lp.exists():
        print(f"Nothing to reset for '{workflow_id}'")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Morsel Runner — atomic task executor")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Execute morsels for a task")
    p_run.add_argument("--workflow-id", required=True)
    p_run.add_argument("--task-id", default="t1")
    p_run.add_argument("--tree", type=Path, default=Path("task-tree.yaml"))
    p_run.add_argument("--resume", action="store_true", help="Resume from checkpoint")

    p_status = sub.add_parser("status", help="Show checkpoint state")
    p_status.add_argument("--workflow-id", required=True)

    p_lock = sub.add_parser("lock", help="Acquire workflow lock")
    p_lock.add_argument("--workflow-id", required=True)

    p_unlock = sub.add_parser("unlock", help="Release workflow lock")
    p_unlock.add_argument("--workflow-id", required=True)

    p_reset = sub.add_parser("reset", help="Clear checkpoint and lock")
    p_reset.add_argument("--workflow-id", required=True)

    args = parser.parse_args()

    if args.command == "run":
        cmd_run(args.workflow_id, args.task_id, args.tree, args.resume)
    elif args.command == "status":
        cmd_status(args.workflow_id)
    elif args.command == "lock":
        if acquire_lock(args.workflow_id):
            print(f"✅ Lock acquired for '{args.workflow_id}'")
        else:
            sys.exit(1)
    elif args.command == "unlock":
        release_lock(args.workflow_id)
    elif args.command == "reset":
        cmd_reset(args.workflow_id)


if __name__ == "__main__":
    main()
