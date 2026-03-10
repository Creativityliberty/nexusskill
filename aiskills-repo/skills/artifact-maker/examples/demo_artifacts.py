"""
Artifact Maker — Demo
=======================
Demonstrates all artifact formats.

Run: python demo_artifacts.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from artifact_engine import ArtifactEngine


def demo():
    print("=" * 60)
    print("  ARTIFACT MAKER — Demo")
    print("=" * 60)

    engine = ArtifactEngine(output_dir="./demo_output")

    # 1. Markdown
    engine.render("markdown", 
                  filename="report.md",
                  title="Project Status Report",
                  content="## Summary\n\nThe project is **on track**.\n\n"
                          "### Key Metrics\n- Velocity: 42 pts/sprint\n"
                          "- Quality: 98% test pass rate\n- Morale: High 🚀\n\n"
                          "### Next Steps\n- Complete API integration\n"
                          "- Deploy to staging\n- Run load tests")

    # 2. JSON
    engine.render("json",
                  filename="metrics.json",
                  data={
                      "sprint": 12,
                      "velocity": 42,
                      "bugs_fixed": 15,
                      "features_shipped": 8,
                      "test_coverage": 94.2
                  })

    # 3. YAML
    engine.render("yaml",
                  filename="config.yaml",
                  data={
                      "project": "Nanoclaw",
                      "version": "2.0",
                      "skills": ["blueprint-maker", "dag-taskview", "artifact-maker"],
                      "settings": {"dark_mode": True, "auto_export": True}
                  })

    # 4. CSV
    engine.render("csv",
                  filename="tasks.csv",
                  headers=["Task", "Status", "Priority", "Assignee"],
                  rows=[
                      ["Design API", "Done", "High", "Alice"],
                      ["Build Auth", "In Progress", "High", "Bob"],
                      ["Write Tests", "Pending", "Medium", "Carol"],
                      ["Deploy", "Blocked", "High", "Dave"],
                  ])

    # 5. HTML
    engine.render("html",
                  filename="dashboard.html",
                  title="Project Dashboard",
                  content="<h2>Sprint 12 Progress</h2>"
                          "<p>Velocity: <strong>42 points</strong></p>"
                          "<p>Test Coverage: <strong>94.2%</strong></p>"
                          "<p style='color: #22c55e;'>Status: ON TRACK ✅</p>")

    # 6. Code
    engine.render("code",
                  filename="generated_api.py",
                  language="python",
                  content='"""Auto-generated API endpoint."""\n\n'
                          'from fastapi import FastAPI\n\n'
                          'app = FastAPI(title="Generated API")\n\n'
                          '@app.get("/health")\n'
                          'async def health():\n'
                          '    return {"status": "ok"}\n')

    # 7. PDF (needs fpdf2)
    try:
        engine.render("pdf",
                      filename="report.pdf",
                      title="Quarterly Report",
                      content="# Executive Summary\n\n"
                              "The project has made significant progress this quarter.\n\n"
                              "## Key Achievements\n"
                              "- Shipped 3 major features\n"
                              "- Reduced bug count by 60%\n"
                              "- Onboarded 2 new team members\n\n"
                              "## Next Quarter Goals\n"
                              "- Launch v2.0\n"
                              "- Achieve 99.9% uptime\n"
                              "- Expand to 3 new markets")
    except Exception as e:
        print(f"  ⚠️ PDF skipped: {e}")

    # 8. Chart (needs matplotlib)
    try:
        engine.render("chart",
                      filename="growth.png",
                      chart_type="bar",
                      title="Monthly Active Users",
                      data={
                          "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                          "values": [1200, 1800, 2400, 3100, 4200, 5800]
                      })
    except Exception as e:
        print(f"  ⚠️ Chart skipped: {e}")

    # Save manifest
    engine.save_manifest()
    engine.summary()

    # Cleanup
    import shutil
    if os.path.exists("./demo_output"):
        shutil.rmtree("./demo_output")
        print("🗑️ Demo output cleaned up")
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    demo()
