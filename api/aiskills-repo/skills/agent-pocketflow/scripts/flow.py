"""
Flow Engine — Orchestrates sequential node execution with dashboard.

Runs nodes in order, tracks progress, generates ASCII dashboard,
and handles errors per-node.

Usage:
    flow = Flow([NodeA(), NodeB(), NodeC()], name="My Pipeline")
    result = flow.run({"input": "data"})
"""

import time
from datetime import datetime, timedelta


class Flow:
    """Sequential flow engine with ASCII progress dashboard."""

    def __init__(self, nodes, name="PocketFlow Agent", api_key=None):
        self.nodes = nodes
        self.name = name

    def run(self, context=None):
        """Execute all nodes in sequence with progress tracking."""
        context = context or {}
        start = time.time()

        # Init flow state
        context["flow"] = {
            "name": self.name,
            "node_count": len(self.nodes),
            "current_node": 0,
            "completed_nodes": [],
            "status": "running",
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        print(self._header())

        for i, node in enumerate(self.nodes):
            node_start = time.time()
            context["flow"]["current_node"] = i + 1
            context["flow"]["current_node_name"] = node.name

            # Progress display
            elapsed = time.time() - start
            context["flow"]["elapsed_time"] = str(timedelta(seconds=int(elapsed)))
            print(self._progress(context))
            print(f"  [{i+1}/{len(self.nodes)}] ⏳ {node.name}")

            try:
                result = node.exec(context)
                node_elapsed = time.time() - node_start

                context[f"result_{node.name}"] = result
                context["flow"]["completed_nodes"].append({
                    "name": node.name,
                    "status": "success",
                    "elapsed": round(node_elapsed, 2),
                })
                print(f"  [{i+1}/{len(self.nodes)}] ✅ {node.name} ({node_elapsed:.2f}s)")

            except Exception as e:
                node_elapsed = time.time() - node_start
                context["flow"]["completed_nodes"].append({
                    "name": node.name,
                    "status": "error",
                    "error": str(e),
                    "elapsed": round(node_elapsed, 2),
                })
                context["flow"]["status"] = "error"
                print(f"  [{i+1}/{len(self.nodes)}] ❌ {node.name}: {e}")
                break

        # Finalize
        if context["flow"]["status"] != "error":
            context["flow"]["status"] = "completed"

        total = time.time() - start
        context["flow"]["elapsed_time"] = str(timedelta(seconds=int(total)))
        context["flow"]["total_seconds"] = round(total, 2)

        print(self._footer(context))
        return context

    def _header(self):
        w = 58
        return f"""
╔{'═' * w}╗
║  🔷 {self.name:<{w-5}}║
╠{'═' * w}╣
║  PocketFlow + Nüm Agents — Hybrid Agent{' ' * (w-41)}║
╚{'═' * w}╝"""

    def _progress(self, ctx):
        current = ctx["flow"]["current_node"]
        total = ctx["flow"]["node_count"]
        node_name = ctx["flow"].get("current_node_name", "")
        elapsed = ctx["flow"]["elapsed_time"]

        bar_width = 40
        filled = int(bar_width * (current - 1) / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)

        return f"  [{bar}] {current}/{total} | ⏱ {elapsed} | ▶ {node_name}"

    def _footer(self, ctx):
        status = ctx["flow"]["status"]
        elapsed = ctx["flow"]["elapsed_time"]
        total = len(ctx["flow"]["completed_nodes"])
        success = sum(1 for n in ctx["flow"]["completed_nodes"] if n["status"] == "success")
        errors = sum(1 for n in ctx["flow"]["completed_nodes"] if n["status"] == "error")
        rate = (success / total * 100) if total > 0 else 0

        emoji = "✅" if status == "completed" else "❌"
        w = 58

        lines = [
            f"\n╔{'═' * w}╗",
            f"║  {emoji} {self.name} — {'COMPLETE' if status == 'completed' else 'FAILED':<{w-6}}║",
            f"╠{'═' * w}╣",
            f"║  ⏱  Time: {elapsed:<{w-12}}║",
            f"║  📊 Nodes: {success}/{total} passed ({rate:.0f}%){' ' * (w-31-len(str(success))-len(str(total)))}║",
        ]

        # Node status
        lines.append(f"╠{'═' * w}╣")
        for node in ctx["flow"]["completed_nodes"]:
            icon = "✅" if node["status"] == "success" else "❌"
            entry = f"  {icon} {node['name']} ({node['elapsed']}s)"
            lines.append(f"║{entry:<{w}}║")

        # Errors
        error_nodes = [n for n in ctx["flow"]["completed_nodes"] if n["status"] == "error"]
        if error_nodes:
            lines.append(f"╠{'═' * w}╣")
            for n in error_nodes:
                err_msg = f"  ⚠️  {n['name']}: {n.get('error', '?')}"[:w]
                lines.append(f"║{err_msg:<{w}}║")

        lines.append(f"╚{'═' * w}╝")
        return "\n".join(lines)
