"""
DAG TaskView — Example Usage
==============================
Demonstrates both standalone DAG creation and chaining from blueprint-maker.

Run:
    python sample_dag.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from dag_engine import DAGEngine


def example_manual():
    """Build a DAG manually."""
    print("\n📌 Example 1: Manual DAG Construction\n")
    
    engine = DAGEngine(project_name="E-Commerce Platform")
    
    # Add tasks
    engine.add_task("design",      "Design System Architecture",    status="done")
    engine.add_task("db",          "Setup Database",                status="done",        deps=["design"])
    engine.add_task("auth",        "Build Authentication",          status="in_progress", deps=["db"])
    engine.add_task("products",    "Product Catalog API",           status="in_progress", deps=["db"])
    engine.add_task("cart",        "Shopping Cart",                 status="pending",     deps=["products", "auth"])
    engine.add_task("payments",    "Payment Integration",           status="pending",     deps=["cart"])
    engine.add_task("orders",      "Order Management",              status="blocked",     deps=["payments", "cart"])
    engine.add_task("frontend",    "Build Frontend",                status="pending",     deps=["products", "auth"])
    engine.add_task("testing",     "Integration Tests",             status="pending",     deps=["orders", "frontend"])
    engine.add_task("deploy",      "Deploy to Production",          status="pending",     deps=["testing"])
    
    # Validate
    valid, errors = engine.validate()
    print(f"  Valid: {valid}")
    if errors:
        for e in errors:
            print(f"  Error: {e}")
    
    # Render
    content = engine.render()
    print(content)
    
    # Summary
    engine.summary()


def example_from_yaml():
    """Load DAG from YAML template."""
    print("\n📌 Example 2: DAG from YAML\n")
    
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'task_template.yaml')
    
    engine = DAGEngine()
    engine.load_yaml(template_path)
    
    content = engine.render()
    print(content)
    engine.summary()


def example_cycle_detection():
    """Demonstrate cycle detection."""
    print("\n📌 Example 3: Cycle Detection\n")
    
    engine = DAGEngine(project_name="Cyclic Test")
    engine.add_task("a", "Task A", deps=["c"])  # A depends on C
    engine.add_task("b", "Task B", deps=["a"])  # B depends on A
    engine.add_task("c", "Task C", deps=["b"])  # C depends on B → CYCLE!
    
    valid, errors = engine.validate()
    print(f"  Valid: {valid}")
    for e in errors:
        print(f"  ⚠️ {e}")


def example_critical_path():
    """Show critical path analysis."""
    print("\n📌 Example 4: Critical Path Analysis\n")
    
    engine = DAGEngine(project_name="Software Release")
    engine.add_task("spec",    "Write Spec",       deps=[])
    engine.add_task("design",  "Design",           deps=["spec"])
    engine.add_task("code",    "Implement",        deps=["design"])
    engine.add_task("docs",    "Documentation",    deps=["spec"])
    engine.add_task("review",  "Code Review",      deps=["code"])
    engine.add_task("test",    "Testing",          deps=["review"])
    engine.add_task("release", "Release",          deps=["test", "docs"])
    
    cp = engine.critical_path()
    cp_names = [engine.tasks[t]["name"] for t in cp]
    print(f"  Critical Path: {' → '.join(cp_names)}")
    print(f"  Length: {len(cp)} steps")
    
    print(f"\n  Next actions: {[engine.tasks[a]['name'] for a in engine.next_actions()]}")


if __name__ == "__main__":
    print("=" * 60)
    print("  DAG TASKVIEW — Examples")
    print("=" * 60)
    
    example_manual()
    example_from_yaml()
    example_cycle_detection()
    example_critical_path()
    
    print("\n✅ All examples completed!")
