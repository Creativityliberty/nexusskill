---
name: artifact-maker
description: Multi-format output engine for AI agents. Converts agent results into real artifacts — Markdown, JSON, PDF reports, charts/images, audio (TTS), video slideshows, and code files. Produces a manifest tracking all outputs. Use when user says "export", "generate report", "create PDF", "make chart", "render output", "save artifacts", "/artifacts".
---

# Artifact Maker — Multi-Format Output Engine

Transforms raw agent output into **production-ready artifacts** in any format.

## When to use

- Agent has produced results that need to be **exported** to a real file
- User wants a **PDF report**, **chart**, **audio narration**, or **video**
- You need to track multiple outputs with a **manifest**

## Supported Formats

| Format | Module | Use Case |
|--------|--------|----------|
| **Markdown** | `markdown_renderer` | Reports, docs, READMEs |
| **JSON / YAML / CSV** | `artifact_engine` (built-in) | Data, configs, tables |
| **PDF** | `pdf_renderer` | Formal reports, invoices |
| **PNG / SVG** | `chart_renderer` | Charts, diagrams, Mermaid |
| **Audio** | `audio_renderer` | TTS voice narration |
| **Video** | `video_renderer` | Slideshow from images + audio |
| **HTML** | `artifact_engine` (Jinja2) | Web-ready pages |
| **Code** | `artifact_engine` (built-in) | .py, .js, .ts with syntax |

## Quick Start

```python
from scripts.artifact_engine import ArtifactEngine

engine = ArtifactEngine(output_dir="./output")

# Generate markdown
engine.render("markdown", content="# My Report\n\nResults here...", filename="report.md")

# Generate PDF
engine.render("pdf", title="Project Report", content="Full analysis...", filename="report.pdf")

# Generate chart
engine.render("chart", data={"labels": ["Q1","Q2","Q3"], "values": [10,25,40]}, filename="growth.png")

# Generate audio (TTS)
engine.render("audio", text="Here are the key findings...", filename="summary.mp3")

# Get manifest of all artifacts
manifest = engine.manifest()
engine.save_manifest("manifest.json")
```

## Step-by-Step

### 1. Initialize engine

```python
engine = ArtifactEngine(output_dir="./artifacts")
```

### 2. Render artifacts

Call `engine.render(format, **kwargs)` for each output you need. The engine auto-detects the right renderer.

### 3. Get manifest

```python
manifest = engine.manifest()
# Returns: {"run_id": "...", "artifacts": [...], "created": "..."}
```

### 4. Chain from other skills

```python
# After blueprint-maker
engine.render("pdf", title=blueprint["meta"]["project_name"], 
              content=blueprint_markdown, filename="blueprint.pdf")

# After dag-taskview
engine.render("chart", mermaid_code=dag_mermaid, filename="dag.svg")
```

## Integration

| Skill | Chain |
|---|---|
| `blueprint-maker` | Blueprint → PDF report + Mermaid diagram |
| `dag-taskview` | DAG → SVG/PNG chart |
| `flow-orchestrator` | Trace → Timeline chart + JSON export |
| `orchestra-forge` | Agent config → YAML export |
| `nanoclaw-ui` | Artifact gallery renders all outputs |

## Renderers

Each renderer lives in `scripts/renderers/` and follows a simple interface:

```python
class BaseRenderer:
    def render(self, output_dir, filename, **kwargs) -> dict:
        """Returns artifact metadata dict."""
```

## Dependencies

Install as needed:

```bash
pip install fpdf2        # PDF generation
pip install matplotlib   # Charts
pip install gtts         # Text-to-Speech
pip install jinja2       # HTML templates
pip install pyyaml       # YAML export
# Optional: ffmpeg for video
```
