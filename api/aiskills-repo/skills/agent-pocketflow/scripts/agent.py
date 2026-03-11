#!/usr/bin/env python3
"""
Agent PocketFlow — Main entry point.

Wires all nodes into flows and provides a CLI for running them.
Combines PocketFlow's Flow engine with Nüm Agents' YAML spec.

Usage:
    python agent.py --test-mode                   # Test all nodes
    python agent.py --flow full-update             # Full pipeline
    python agent.py --flow dm-log --test-mode      # DM-Log only (test)
    python agent.py --provider openai              # Use OpenAI
"""

import sys
import os
import argparse
import yaml

# Ensure scripts dir is in path
sys.path.insert(0, os.path.dirname(__file__))

from flow import Flow
from nodes.base_node import BaseNode
from nodes.git_nodes import GitCommitNode, GitPushNode
from nodes.doc_nodes import (
    DMLogParserNode, DMLogLLMNode, DMLogUpdateNode,
    ModelConceptUpdateNode, ProjectStructureUpdateNode,
    TasksUpdateNode, RequirementsUpdateNode,
)


def load_agent_spec():
    """Load agent.yaml Nüm Agents spec."""
    spec_path = os.path.join(os.path.dirname(__file__), "..", "agent.yaml")
    if os.path.exists(spec_path):
        with open(spec_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return None


def create_flow(flow_name="full-update", provider="gemini", api_key=None, test_mode=False):
    """
    Create a flow by name, matching the Nüm Agents spec.

    Available flows: full-update, dm-log, mcd-update
    """
    common = dict(api_key=api_key, provider=provider, test_mode=test_mode)

    flows = {
        "full-update": lambda: Flow([
            GitCommitNode(),
            DMLogParserNode(),
            DMLogLLMNode(**common),
            DMLogUpdateNode(),
            ModelConceptUpdateNode(**common),
            ProjectStructureUpdateNode(**common),
            TasksUpdateNode(**common),
            RequirementsUpdateNode(**common),
            GitPushNode(files=[
                "docs/dm-log.md", "docs/mcd-guardrails.md",
                "docs/project-structure.md", "docs/tasks.md",
                "docs/requirements.md",
            ]),
        ], name="DocUpdate Agent — Full Pipeline"),

        "dm-log": lambda: Flow([
            GitCommitNode(),
            DMLogParserNode(),
            DMLogLLMNode(**common),
            DMLogUpdateNode(),
            GitPushNode(files=["docs/dm-log.md"]),
        ], name="DocUpdate Agent — DM-Log Only"),

        "mcd-update": lambda: Flow([
            ModelConceptUpdateNode(**common),
            GitPushNode(files=["docs/mcd-guardrails.md"]),
        ], name="DocUpdate Agent — MCD Only"),
    }

    if flow_name not in flows:
        print(f"❌ Unknown flow: {flow_name}")
        print(f"   Available: {', '.join(flows.keys())}")
        sys.exit(1)

    return flows[flow_name]()


def main():
    parser = argparse.ArgumentParser(
        description="Agent PocketFlow — Hybrid PocketFlow + Nüm Agents Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py --test-mode                    Test run (no API key needed)
  python agent.py --flow dm-log --test-mode      DM-Log only (test mode)
  python agent.py --provider gemini              Full update with Gemini
  python agent.py --flow mcd-update              MCD update only
        """,
    )
    parser.add_argument("--flow", default="full-update",
                        choices=["full-update", "dm-log", "mcd-update"],
                        help="Flow to execute (default: full-update)")
    parser.add_argument("--provider", default="gemini",
                        choices=["gemini", "openai", "deepseek"],
                        help="LLM provider (default: gemini)")
    parser.add_argument("--api-key", default=None,
                        help="API key (or set env variable)")
    parser.add_argument("--test-mode", action="store_true",
                        help="Run in test mode (no API calls)")
    parser.add_argument("--show-spec", action="store_true",
                        help="Show agent.yaml spec and exit")

    args = parser.parse_args()

    # Show spec
    if args.show_spec:
        spec = load_agent_spec()
        if spec:
            print(yaml.dump(spec, default_flow_style=False, allow_unicode=True))
        else:
            print("⚠️ agent.yaml not found")
        return

    # Print agent info
    spec = load_agent_spec()
    if spec:
        agent_info = spec.get("agent", {})
        print(f"\n  🤖 Agent: {agent_info.get('name', 'Unknown')}")
        print(f"  📝 {agent_info.get('description', '')}")
        univers = agent_info.get("univers", [])
        if univers:
            print(f"  🌌 Universes: {', '.join(univers)}")
        print()

    # Create and run flow
    flow = create_flow(
        flow_name=args.flow,
        provider=args.provider,
        api_key=args.api_key,
        test_mode=args.test_mode,
    )

    result = flow.run()

    # Summary
    status = result["flow"]["status"]
    if status == "completed":
        print("\n  🎉 Pipeline completed successfully!\n")
    else:
        print("\n  ❌ Pipeline failed. Check errors above.\n")

    return 0 if status == "completed" else 1


if __name__ == "__main__":
    sys.exit(main() or 0)
