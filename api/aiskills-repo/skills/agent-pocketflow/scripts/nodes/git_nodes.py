"""
Git Nodes — Nodes for Git operations.

GitCommitNode: reads last commit info
GitPushNode: stages, commits, and pushes changes
"""

import datetime
import subprocess
from nodes.base_node import BaseNode


class GitCommitNode(BaseNode):
    """Reads the latest Git commit info and populates context."""

    def __init__(self):
        super().__init__("git_commit")

    def exec(self, context: dict) -> dict:
        try:
            msg = subprocess.check_output(
                ["git", "log", "-1", "--pretty=%B"],
                text=True, timeout=10
            ).strip()
        except Exception:
            msg = "No git history available"

        context["task_name"] = msg.split("\n")[0]
        context["today"] = datetime.date.today().isoformat()

        if "task_results" not in context:
            context["task_results"] = ["Task executed successfully"]
        if "next_steps" not in context:
            context["next_steps"] = ["Continue development"]

        return context


class GitPushNode(BaseNode):
    """Stages, commits, and pushes specified files."""

    def __init__(self, files: list = None, commit_message: str = None):
        super().__init__("git_push")
        self.files = files or ["docs/"]
        self.commit_message = commit_message

    def exec(self, context: dict) -> bool:
        date = context.get("today", datetime.date.today().isoformat())
        message = self.commit_message or f"Auto-update docs: {date}"

        try:
            for f in self.files:
                subprocess.check_call(["git", "add", f], timeout=10)
            subprocess.check_call(["git", "commit", "-m", message], timeout=10)
            subprocess.check_call(["git", "push"], timeout=30)
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️ Git push skipped: {e}")
            return False
