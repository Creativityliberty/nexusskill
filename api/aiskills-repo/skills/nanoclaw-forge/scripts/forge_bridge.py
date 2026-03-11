"""
Nanoclaw Forge Bridge
======================
Programmatic bridge that imports and chains all Nanoclaw skill engines
into one unified 5-phase pipeline: PLAN → MAP → BUILD → RUN → SHIP.

Usage:
    from forge_bridge import NanoclawForge
    
    forge = NanoclawForge()
    results = forge.full_pipeline("Build a fitness tracking app", constraints="6 months, $50k")
    # Or run individual phases:
    blueprint = forge.plan("Build a fitness app")
    dag = forge.map(blueprint)
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add all skill script dirs to path
SKILLS_DIR = Path(__file__).parent.parent.parent
for skill_dir in SKILLS_DIR.iterdir():
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        sys.path.insert(0, str(scripts_dir))


class NanoclawForge:
    """
    Unified pipeline that fuses all Nanoclaw skills.
    
    Phases:
        1. PLAN  — blueprint-maker  → structured blueprint
        2. MAP   — dag-taskview     → DAG with dependencies
        3. BUILD — orchestra-forge  → agent.yaml + agent.py
        4. RUN   — flow-orchestrator → traced execution
        5. SHIP  — artifact-maker   → PDF, charts, audit
    """

    def __init__(self, output_dir="./forge_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.state = {
            "started": datetime.now().isoformat(),
            "phases_completed": [],
            "blueprint": None,
            "dag": None,
            "agent": None,
            "trace": None,
            "artifacts": None,
        }

    # -------------------------------------------------------------------
    # Phase 1: PLAN
    # -------------------------------------------------------------------
    def plan(self, goal, constraints="", audience="", domain="auto"):
        """
        Phase 1: Generate a structured blueprint using blueprint-maker.
        
        Args:
            goal: What the user wants to build
            constraints: Budget, timeline, resource limits
            audience: Target audience
            domain: auto-detect or specify (business/product/research/education/engineering)
        """
        print("\n" + "=" * 60)
        print("  🏗️  PHASE 1: PLAN (blueprint-maker)")
        print("=" * 60)

        from blueprint_engine import BlueprintEngine

        engine = BlueprintEngine()

        if domain == "auto":
            domain = engine.detect_domain(goal)
            print(f"  🔍 Auto-detected domain: {domain}")

        blueprint = engine.generate(
            domain=domain,
            goal=goal,
            constraints=constraints,
            audience=audience,
        )

        # Export
        bp_path = self.output_dir / "blueprint.md"
        engine.export(blueprint, str(bp_path), fmt="markdown")

        self.state["blueprint"] = blueprint
        self.state["phases_completed"].append("PLAN")

        print(f"  ✅ Blueprint: {len(blueprint['sections'])} sections")
        print(f"  📄 Saved to: {bp_path}")
        return blueprint

    # -------------------------------------------------------------------
    # Phase 2: MAP
    # -------------------------------------------------------------------
    def map(self, blueprint=None):
        """
        Phase 2: Convert blueprint into a DAG with dependencies.
        
        Args:
            blueprint: Blueprint dict from Phase 1 (or uses stored state)
        """
        print("\n" + "=" * 60)
        print("  🌲  PHASE 2: MAP (dag-taskview)")
        print("=" * 60)

        bp = blueprint or self.state.get("blueprint")
        if not bp:
            raise ValueError("No blueprint found. Run Phase 1 (plan) first.")

        from blueprint_engine import BlueprintEngine
        from dag_engine import DAGEngine

        # Convert blueprint to task list
        bp_engine = BlueprintEngine()
        tasks = bp_engine.to_dag_tasks(bp)

        # Build DAG
        dag = DAGEngine(project_name=bp["meta"]["project_name"])
        dag.load_dict(tasks, project_name=bp["meta"]["project_name"])

        # Validate
        valid, errors = dag.validate()
        if not valid:
            print(f"  ⚠️ DAG warnings: {errors}")

        # Render
        dag_path = self.output_dir / "dag.md"
        dag.render(str(dag_path))
        dag.summary()

        self.state["dag"] = {
            "engine": dag,
            "tasks": tasks,
            "critical_path": dag.critical_path(),
            "progress": dag.progress(),
        }
        self.state["phases_completed"].append("MAP")

        print(f"  ✅ DAG: {len(tasks)} tasks")
        print(f"  🔥 Critical path: {len(dag.critical_path())} steps")
        return dag

    # -------------------------------------------------------------------
    # Phase 3: BUILD
    # -------------------------------------------------------------------
    def build(self, dag=None, mode="single"):
        """
        Phase 3: Generate agent code from DAG tasks.
        
        Args:
            dag: DAGEngine from Phase 2 (or uses stored state)
            mode: "single" (orchestra-forge) or "kernel" (kernel-forge)
        """
        print("\n" + "=" * 60)
        print(f"  ⚙️  PHASE 3: BUILD ({'orchestra-forge' if mode == 'single' else 'kernel-forge'})")
        print("=" * 60)

        dag_state = self.state.get("dag") if dag is None else {"engine": dag}
        if not dag_state:
            raise ValueError("No DAG found. Run Phase 2 (map) first.")

        dag_engine = dag_state["engine"] if isinstance(dag_state, dict) else dag

        # Generate agent.yaml from DAG tasks
        agent_yaml = self._generate_agent_yaml(dag_engine, mode)

        # Generate agent.py (PocketFlow nodes)
        agent_code = self._generate_agent_code(dag_engine, mode)

        # Save files
        yaml_path = self.output_dir / "agent.yaml"
        py_path = self.output_dir / "agent.py"

        import yaml
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(agent_yaml, f, default_flow_style=False, allow_unicode=True)

        with open(py_path, 'w', encoding='utf-8') as f:
            f.write(agent_code)

        self.state["agent"] = {
            "yaml": agent_yaml,
            "code": agent_code,
            "mode": mode,
        }
        self.state["phases_completed"].append("BUILD")

        print(f"  ✅ agent.yaml: {len(agent_yaml.get('flows', [{}])[0].get('nodes', []))} nodes")
        print(f"  ✅ agent.py: {len(agent_code)} chars")
        print(f"  📄 Saved to: {yaml_path}, {py_path}")
        return agent_yaml, agent_code

    def _generate_agent_yaml(self, dag_engine, mode):
        """Generate a Nüm Agents YAML spec from DAG."""
        nodes = []
        transitions = []
        prev_id = None

        for tid in dag_engine.task_order:
            task = dag_engine.tasks[tid]
            node_name = tid.replace("-", "_").replace(" ", "_").title().replace("_", "")
            nodes.append(node_name)

            if task["deps"]:
                for dep in task["deps"]:
                    dep_name = dep.replace("-", "_").replace(" ", "_").title().replace("_", "")
                    transitions.append({
                        "from": dep_name,
                        "to": node_name,
                        "on": "default"
                    })
            prev_id = tid

        spec = {
            "agent": {
                "name": dag_engine.project_name.replace(" ", ""),
                "description": f"Auto-generated agent for: {dag_engine.project_name}",
                "univers": ["PocketFlowCore", "StructureAgentIA"],
                "protocol": "N2A",
                "llm": "gemini-2.5-flash",
                "memory": False,
                "tracing": True,
            },
            "flows": [{
                "name": "main",
                "nodes": nodes,
                "transitions": transitions,
            }]
        }
        return spec

    def _generate_agent_code(self, dag_engine, mode):
        """Generate PocketFlow Python code from DAG."""
        lines = [
            '"""',
            f'Agent: {dag_engine.project_name}',
            f'Generated by Nanoclaw Forge — {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            '"""',
            '',
            'import sys',
            'sys.path.insert(0, ".")',
            '',
            'try:',
            '    from pocketflow import Node, Flow',
            'except ImportError:',
            '    # Minimal fallback',
            '    class Node:',
            '        def prep(self, shared): return None',
            '        def exec(self, prep_res): return None',
            '        def post(self, shared, prep_res, exec_res): return "default"',
            '        def __rshift__(self, other): return other',
            '    class Flow:',
            '        def __init__(self, start=None): self.start = start',
            '        def run(self, shared): print("Flow executed")',
            '',
            '',
            '# --- Nodes ---',
            '',
        ]

        # Generate a Node class for each DAG task
        for tid in dag_engine.task_order:
            task = dag_engine.tasks[tid]
            class_name = tid.replace("-", "_").replace(" ", "_").title().replace("_", "")

            lines.extend([
                f'class {class_name}(Node):',
                f'    """{task["name"]}"""',
                '',
                '    def prep(self, shared):',
                f'        return shared.get("{tid}_input", None)',
                '',
                '    def exec(self, prep_res):',
                f'        print(f"  ▶ Executing: {task["name"]}")',
                f'        # TODO: Implement {task["name"]} logic',
                '        return {"status": "done"}',
                '',
                '    def post(self, shared, prep_res, exec_res):',
                f'        shared["{tid}_output"] = exec_res',
                '        return "default"',
                '',
                '',
            ])

        # Wire the flow
        lines.append('# --- Flow Wiring ---')
        lines.append('')

        node_vars = []
        for tid in dag_engine.task_order:
            var_name = tid.replace("-", "_")
            class_name = tid.replace("-", "_").replace(" ", "_").title().replace("_", "")
            lines.append(f'{var_name} = {class_name}()')
            node_vars.append(var_name)

        lines.append('')

        # Wire transitions
        for tid in dag_engine.task_order:
            task = dag_engine.tasks[tid]
            var_name = tid.replace("-", "_")
            for dep in task["deps"]:
                dep_var = dep.replace("-", "_")
                lines.append(f'{dep_var} >> {var_name}')

        lines.append('')
        if node_vars:
            lines.append(f'flow = Flow(start={node_vars[0]})')
        else:
            lines.append('flow = Flow()')

        lines.extend([
            '',
            '',
            '# --- Run ---',
            '',
            'if __name__ == "__main__":',
            '    shared = {"goal": "Execute pipeline"}',
            '    flow.run(shared)',
            '    print("\\n✅ Pipeline complete!")',
            '    print(f"Results: {json.dumps(shared, indent=2, default=str)}")',
            '',
        ])

        return '\n'.join(lines)

    # -------------------------------------------------------------------
    # Phase 4: RUN
    # -------------------------------------------------------------------
    def run(self, agent=None):
        """
        Phase 4: Execute the agent with tracing.
        
        Note: This phase typically requires manual setup.
        The forge generates the trace configuration and run script.
        """
        print("\n" + "=" * 60)
        print("  ⚡  PHASE 4: RUN (flow-orchestrator)")
        print("=" * 60)

        agent_state = agent or self.state.get("agent")
        if not agent_state:
            raise ValueError("No agent found. Run Phase 3 (build) first.")

        # Generate run configuration
        run_config = {
            "pipeline": agent_state.get("yaml", {}).get("agent", {}).get("name", "forge-agent"),
            "tracing": True,
            "snapshot": True,
            "timestamp": datetime.now().isoformat(),
        }

        config_path = self.output_dir / "run_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(run_config, f, indent=2)

        self.state["trace"] = run_config
        self.state["phases_completed"].append("RUN")

        print(f"  ✅ Run config generated")
        print(f"  📄 Config: {config_path}")
        print(f"  💡 Execute: python {self.output_dir / 'agent.py'}")
        return run_config

    # -------------------------------------------------------------------
    # Phase 5: SHIP
    # -------------------------------------------------------------------
    def ship(self, results=None):
        """
        Phase 5: Export artifacts + quality audit.
        """
        print("\n" + "=" * 60)
        print("  📦  PHASE 5: SHIP (artifact-maker + skill-architect)")
        print("=" * 60)

        from artifact_engine import ArtifactEngine

        art = ArtifactEngine(output_dir=str(self.output_dir / "artifacts"))

        # Export blueprint as markdown
        bp = self.state.get("blueprint")
        if bp:
            from blueprint_engine import BlueprintEngine
            bp_engine = BlueprintEngine()
            md_content = bp_engine._to_markdown(bp)
            art.render("markdown", filename="blueprint.md", content=md_content)

            # Export as PDF
            try:
                art.render("pdf", filename="blueprint.pdf", title=bp["meta"]["project_name"],
                           content=md_content)
            except Exception as e:
                print(f"  ⚠️ PDF export skipped: {e}")

        # Export DAG
        dag_state = self.state.get("dag")
        if dag_state and hasattr(dag_state.get("engine"), "to_mermaid"):
            dag_engine = dag_state["engine"]
            mermaid_code = dag_engine.to_mermaid()
            art.render("chart", filename="dag.html", mermaid_code=mermaid_code)

        # Export agent code as artifact
        agent_state = self.state.get("agent")
        if agent_state:
            art.render("code", filename="agent.py", content=agent_state.get("code", ""))
            art.render("yaml", filename="agent.yaml", data=agent_state.get("yaml", {}))

        # Export pipeline state
        art.render("json", filename="pipeline_state.json", data={
            "phases_completed": self.state["phases_completed"],
            "started": self.state["started"],
            "completed": datetime.now().isoformat(),
        })

        art.save_manifest()
        art.summary()

        self.state["artifacts"] = art.manifest()
        self.state["phases_completed"].append("SHIP")

        print(f"  ✅ {len(art.artifacts)} artifacts exported")
        return art.manifest()

    # -------------------------------------------------------------------
    # Full Pipeline
    # -------------------------------------------------------------------
    def full_pipeline(self, goal, constraints="", audience="", domain="auto",
                      build_mode="single"):
        """
        Run all 5 phases end-to-end.
        
        Args:
            goal: What to build
            constraints: Budget/timeline
            audience: Target audience
            domain: Auto or specific
            build_mode: "single" or "kernel"
        """
        print("\n" + "🔷" * 30)
        print("  NANOCLAW FORGE — Full Pipeline")
        print("🔷" * 30)
        print(f"\n  Goal: {goal}")
        print(f"  Constraints: {constraints or 'None'}")
        print(f"  Build mode: {build_mode}\n")

        blueprint = self.plan(goal, constraints, audience, domain)
        dag = self.map(blueprint)
        agent_yaml, agent_code = self.build(dag, mode=build_mode)
        run_config = self.run()
        manifest = self.ship()

        # Final summary
        print("\n" + "=" * 60)
        print("  🎉 NANOCLAW FORGE — COMPLETE")
        print("=" * 60)
        print(f"  Phases: {' → '.join(self.state['phases_completed'])}")
        print(f"  Blueprint: {len(blueprint['sections'])} sections")
        print(f"  DAG: {len(self.state['dag']['tasks'])} tasks")
        print(f"  Agent: {len(agent_yaml['flows'][0]['nodes'])} nodes")
        print(f"  Artifacts: {len(manifest['artifacts'])} files")
        print(f"  Output: {self.output_dir}")
        print("=" * 60)

        return self.state

    # -------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------
    def status(self):
        """Print current pipeline status."""
        print(f"\n{'=' * 50}")
        print(f"  Nanoclaw Forge — Status")
        print(f"{'=' * 50}")
        print(f"  Phases: {', '.join(self.state['phases_completed']) or 'None'}")
        print(f"  Blueprint: {'✅' if self.state['blueprint'] else '⏳'}")
        print(f"  DAG: {'✅' if self.state['dag'] else '⏳'}")
        print(f"  Agent: {'✅' if self.state['agent'] else '⏳'}")
        print(f"  Trace: {'✅' if self.state['trace'] else '⏳'}")
        print(f"  Artifacts: {'✅' if self.state['artifacts'] else '⏳'}")
        print(f"{'=' * 50}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Nanoclaw Forge — Unified Pipeline")
    parser.add_argument("goal", help="What do you want to build?")
    parser.add_argument("--constraints", default="", help="Budget, timeline, resources")
    parser.add_argument("--audience", default="", help="Target audience")
    parser.add_argument("--domain", default="auto", help="Domain: auto/business/product/research/education/engineering")
    parser.add_argument("--mode", default="single", choices=["single", "kernel"], help="Build mode")
    parser.add_argument("--output", default="./forge_output", help="Output directory")
    parser.add_argument("--phases", default="all", help="Phases to run: all, plan, map, build, run, ship (comma-separated)")

    args = parser.parse_args()

    forge = NanoclawForge(output_dir=args.output)

    phases = args.phases.split(",") if args.phases != "all" else ["plan", "map", "build", "run", "ship"]

    if "plan" in phases:
        forge.plan(args.goal, args.constraints, args.audience, args.domain)
    if "map" in phases:
        forge.map()
    if "build" in phases:
        forge.build(mode=args.mode)
    if "run" in phases:
        forge.run()
    if "ship" in phases:
        forge.ship()

    forge.status()


if __name__ == "__main__":
    main()
