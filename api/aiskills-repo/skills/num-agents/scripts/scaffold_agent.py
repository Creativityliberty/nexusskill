#!/usr/bin/env python3
"""
Nüm Agents — Agent Scaffold Helper
====================================
Generates a starter agent.yaml + boilerplate Python from a description.
Run this BEFORE `num-agents generate` to bootstrap your spec.

Usage:
    python scaffold_agent.py --name MyAgent --description "What it does" --universes PocketFlowCore StructureAgentIA
    python scaffold_agent.py --interactive
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

UNIVERSE_CHOICES = [
    "PocketFlowCore",
    "StructureAgentIA",
    "KnowledgeLayer",
    "ConditionalFlow",
    "EventBusUnivers",
    "SchedulerUnivers",
    "APIConnectorUnivers",
    "RAGUnivers",
    "MetricsUnivers",
    "TracingUnivers",
]

UNIVERSE_DESCRIPTIONS = {
    "PocketFlowCore":     "Node/Flow execution engine — always include",
    "StructureAgentIA":   "Structured LLM outputs and reasoning",
    "KnowledgeLayer":     "Memory and retrieval",
    "ConditionalFlow":    "If/else branching in flows",
    "EventBusUnivers":    "Pub/sub inter-agent messaging",
    "SchedulerUnivers":   "Cron scheduling",
    "APIConnectorUnivers":"External HTTP/REST calls",
    "RAGUnivers":         "Full RAG pipeline (ingest→chunk→embed→retrieve)",
    "MetricsUnivers":     "Performance metrics",
    "TracingUnivers":     "Distributed tracing",
}


def generate_yaml(name: str, description: str, universes: list[str],
                  llm: str, memory: bool, eventbus: bool,
                  scheduler: bool, metrics: bool, tracing: bool) -> str:
    univers_block = "\n".join(f"    - {u}" for u in universes)
    protocol = "A2A" if "EventBusUnivers" in universes else "N2A"
    return f"""agent:
  name: "{name}"
  description: "{description}"
  univers:
{univers_block}
  protocol: {protocol}
  llm: {llm}
  memory: {"true" if memory else "false"}
  eventbus: {"true" if eventbus else "false"}
  scheduler: {"true" if scheduler else "false"}
  metrics: {"true" if metrics else "false"}
  tracing: {"true" if tracing else "false"}
"""


def generate_boilerplate(name: str, universes: list[str]) -> str:
    has_conditional = "ConditionalFlow" in universes
    has_async = False  # can be extended

    imports = ["from num_agents import Node, Flow, SharedStore, configure_logging"]
    if has_conditional:
        imports[0] += ", ConditionalNode"
    imports.append("import logging\n")

    return "\n".join(imports) + f"""
configure_logging(level=logging.INFO)
logger = logging.getLogger(__name__)


class Step1Node(Node):
    \"\"\"First step — fetch or prepare input data.\"\"\"
    def __init__(self):
        super().__init__(name="Step1", retry_count=3, enable_logging=True)

    def exec(self, shared: SharedStore):
        # TODO: implement
        data = shared.get("input")
        result = data  # replace with actual logic
        shared.set("step1_result", result)
        return result


class Step2Node(Node):
    \"\"\"Second step — process data.\"\"\"
    def __init__(self):
        super().__init__(name="Step2", enable_logging=True)

    def exec(self, shared: SharedStore):
        # TODO: implement
        data = shared.get("step1_result")
        result = data  # replace with actual logic
        shared.set("step2_result", result)
        return result


def build_flow() -> Flow:
    step1 = Step1Node()
    step2 = Step2Node()

    step1.connect(step2)

    flow = Flow(name="{name}Pipeline", enable_logging=True)
    flow.add_node(step1)
    flow.add_node(step2)
    flow.set_start(step1)
    return flow


if __name__ == "__main__":
    flow = build_flow()
    results = flow.execute(initial_data={{
        "input": "your input here"
    }})
    print(results)
"""


def interactive_mode() -> dict:
    print("\n🤖 Nüm Agents — Interactive Scaffold\n")
    name = input("Agent name (PascalCase): ").strip() or "MyAgent"
    description = input("Description: ").strip() or "An agent built with Nüm Agents SDK"
    llm = input("LLM model [claude-sonnet-4-6]: ").strip() or "claude-sonnet-4-6"

    print("\nAvailable universes:")
    for i, u in enumerate(UNIVERSE_CHOICES, 1):
        print(f"  {i:2d}. {u:<25} — {UNIVERSE_DESCRIPTIONS[u]}")

    raw = input("\nSelect universes (numbers, comma-separated) [1]: ").strip()
    if not raw:
        selected_indices = [1]
    else:
        selected_indices = [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]

    universes = [UNIVERSE_CHOICES[i - 1] for i in selected_indices if 1 <= i <= len(UNIVERSE_CHOICES)]
    if not universes:
        universes = ["PocketFlowCore"]

    memory = input("Enable memory? [y/N]: ").strip().lower() == "y"
    eventbus = input("Enable event bus? [y/N]: ").strip().lower() == "y"
    scheduler = input("Enable scheduler? [y/N]: ").strip().lower() == "y"
    metrics = input("Enable metrics? [y/N]: ").strip().lower() == "y"
    tracing = input("Enable tracing? [y/N]: ").strip().lower() == "y"

    return dict(name=name, description=description, universes=universes,
                llm=llm, memory=memory, eventbus=eventbus,
                scheduler=scheduler, metrics=metrics, tracing=tracing)


def main() -> None:
    parser = argparse.ArgumentParser(description="Nüm Agents scaffold helper")
    parser.add_argument("--name", help="Agent name (PascalCase)")
    parser.add_argument("--description", help="Agent description")
    parser.add_argument("--universes", nargs="+", choices=UNIVERSE_CHOICES,
                        default=["PocketFlowCore"])
    parser.add_argument("--llm", default="claude-sonnet-4-6")
    parser.add_argument("--memory", action="store_true")
    parser.add_argument("--eventbus", action="store_true")
    parser.add_argument("--scheduler", action="store_true")
    parser.add_argument("--metrics", action="store_true")
    parser.add_argument("--tracing", action="store_true")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Interactive mode")
    parser.add_argument("--output", "-o", type=Path, default=Path("."),
                        help="Output directory")
    args = parser.parse_args()

    if args.interactive:
        params = interactive_mode()
    else:
        if not args.name:
            parser.error("--name is required (or use --interactive)")
        params = dict(
            name=args.name,
            description=args.description or f"{args.name} agent",
            universes=args.universes,
            llm=args.llm,
            memory=args.memory,
            eventbus=args.eventbus,
            scheduler=args.scheduler,
            metrics=args.metrics,
            tracing=args.tracing,
        )

    output_dir: Path = args.output if hasattr(args, "output") else Path(".")
    output_dir.mkdir(parents=True, exist_ok=True)

    yaml_content = generate_yaml(**params)
    boilerplate = generate_boilerplate(params["name"], params["universes"])

    yaml_path = output_dir / "agent.yaml"
    agent_path = output_dir / "agent.py"

    yaml_path.write_text(yaml_content, encoding="utf-8")
    agent_path.write_text(boilerplate, encoding="utf-8")

    print(f"\n✅ Generated:")
    print(f"   {yaml_path}  ← run: num-agents generate --spec {yaml_path}")
    print(f"   {agent_path}  ← boilerplate to implement")
    print(f"\nNext: num-agents generate --spec {yaml_path}")


if __name__ == "__main__":
    main()
