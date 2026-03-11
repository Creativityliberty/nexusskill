"""
Artifact Engine
================
Core routing engine for multi-format artifact generation.
Routes content to the right renderer and tracks all outputs in a manifest.

Usage:
    from artifact_engine import ArtifactEngine
    engine = ArtifactEngine(output_dir="./output")
    engine.render("markdown", content="# Report", filename="report.md")
    engine.render("pdf", title="Report", content="...", filename="report.pdf")
    engine.save_manifest("manifest.json")
"""

import json
import yaml
import csv
import os
import uuid
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Artifact Engine
# ---------------------------------------------------------------------------

class ArtifactEngine:
    """
    Routes agent output to the appropriate renderer and tracks artifacts.
    
    Supports: markdown, json, yaml, csv, pdf, chart, audio, video, html, code
    """

    def __init__(self, output_dir="./artifacts", run_id=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id or str(uuid.uuid4())[:8]
        self.artifacts = []
        self.created_at = datetime.now().isoformat()
        self._renderers = {}

    def render(self, fmt, filename, **kwargs):
        """
        Render an artifact in the specified format.
        
        Args:
            fmt: Format type (markdown, json, yaml, csv, pdf, chart, audio, video, html, code)
            filename: Output filename
            **kwargs: Format-specific arguments
        
        Returns:
            dict: Artifact metadata
        """
        filepath = self.output_dir / filename
        
        # Built-in formats (no external deps)
        builtin = {
            "markdown": self._render_markdown,
            "md": self._render_markdown,
            "json": self._render_json,
            "yaml": self._render_yaml,
            "csv": self._render_csv,
            "html": self._render_html,
            "code": self._render_code,
        }
        
        # External renderers (lazy import)
        external = {
            "pdf": self._render_pdf,
            "chart": self._render_chart,
            "image": self._render_chart,
            "audio": self._render_audio,
            "video": self._render_video,
        }
        
        handler = builtin.get(fmt) or external.get(fmt)
        if not handler:
            raise ValueError(f"Unknown format '{fmt}'. Supported: {list(builtin.keys()) + list(external.keys())}")
        
        # Render
        meta = handler(filepath, **kwargs)
        
        # Track artifact
        artifact = {
            "type": fmt,
            "filename": filename,
            "path": str(filepath),
            "size": self._file_size(filepath),
            "created": datetime.now().isoformat(),
            **meta
        }
        self.artifacts.append(artifact)
        
        print(f"  📦 [{fmt.upper()}] {filename} ({artifact['size']})")
        return artifact

    # -----------------------------------------------------------------------
    # Built-in Renderers
    # -----------------------------------------------------------------------

    def _render_markdown(self, filepath, content="", title=None, **kwargs):
        """Render markdown file."""
        if title:
            content = f"# {title}\n\n{content}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"renderer": "builtin"}

    def _render_json(self, filepath, data=None, content=None, indent=2, **kwargs):
        """Render JSON file."""
        if content and not data:
            data = content if isinstance(content, (dict, list)) else {"content": content}
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data or {}, f, indent=indent, ensure_ascii=False)
        return {"renderer": "builtin"}

    def _render_yaml(self, filepath, data=None, content=None, **kwargs):
        """Render YAML file."""
        if content and not data:
            data = content if isinstance(content, dict) else {"content": content}
        
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data or {}, f, default_flow_style=False, allow_unicode=True)
        return {"renderer": "builtin"}

    def _render_csv(self, filepath, rows=None, headers=None, **kwargs):
        """Render CSV file."""
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            if headers:
                writer.writerow(headers)
            if rows:
                writer.writerows(rows)
        return {"renderer": "builtin", "rows": len(rows or [])}

    def _render_html(self, filepath, content="", title="Artifact", template=None, **kwargs):
        """Render HTML file. Optionally uses Jinja2 template."""
        if template:
            try:
                from jinja2 import Template
                with open(template, 'r', encoding='utf-8') as f:
                    tmpl = Template(f.read())
                html = tmpl.render(title=title, content=content, **kwargs)
            except ImportError:
                html = self._basic_html(title, content)
        else:
            html = self._basic_html(title, content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return {"renderer": "html"}

    def _render_code(self, filepath, content="", language=None, **kwargs):
        """Render a code file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        ext = filepath.suffix.lstrip('.')
        return {"renderer": "code", "language": language or ext}

    # -----------------------------------------------------------------------
    # External Renderers (lazy imports)
    # -----------------------------------------------------------------------

    def _render_pdf(self, filepath, title="Report", content="", sections=None, **kwargs):
        """Render PDF using fpdf2."""
        try:
            from renderers.pdf_renderer import PDFRenderer
            renderer = PDFRenderer()
            return renderer.render(str(filepath), title=title, content=content, sections=sections, **kwargs)
        except ImportError:
            # Fallback: simple PDF with fpdf2
            return self._fallback_pdf(filepath, title, content)

    def _render_chart(self, filepath, data=None, chart_type="bar", mermaid_code=None, **kwargs):
        """Render chart/image using matplotlib or Mermaid."""
        try:
            from renderers.chart_renderer import ChartRenderer
            renderer = ChartRenderer()
            return renderer.render(str(filepath), data=data, chart_type=chart_type, 
                                   mermaid_code=mermaid_code, **kwargs)
        except ImportError:
            return self._fallback_chart(filepath, data, chart_type)

    def _render_audio(self, filepath, text="", **kwargs):
        """Render audio using gTTS."""
        try:
            from renderers.audio_renderer import AudioRenderer
            renderer = AudioRenderer()
            return renderer.render(str(filepath), text=text, **kwargs)
        except ImportError:
            return self._fallback_audio(filepath, text)

    def _render_video(self, filepath, images=None, audio=None, **kwargs):
        """Render video using ffmpeg."""
        try:
            from renderers.video_renderer import VideoRenderer
            renderer = VideoRenderer()
            return renderer.render(str(filepath), images=images, audio=audio, **kwargs)
        except ImportError:
            print("  ⚠️ ffmpeg not available. Video rendering skipped.")
            return {"renderer": "video", "status": "skipped", "reason": "ffmpeg not installed"}

    # -----------------------------------------------------------------------
    # Fallbacks (when full renderers not available)
    # -----------------------------------------------------------------------

    def _fallback_pdf(self, filepath, title, content):
        """Simple PDF fallback using fpdf2."""
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 20)
            pdf.cell(0, 15, title, new_x="LMARGIN", new_y="NEXT", align="C")
            pdf.ln(5)
            pdf.set_font("Helvetica", "", 11)
            
            # Handle multi-line content
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('# '):
                    pdf.set_font("Helvetica", "B", 16)
                    pdf.cell(0, 10, line[2:], new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("Helvetica", "", 11)
                elif line.startswith('## '):
                    pdf.set_font("Helvetica", "B", 14)
                    pdf.cell(0, 9, line[3:], new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("Helvetica", "", 11)
                elif line.startswith('- '):
                    pdf.cell(10)
                    pdf.cell(0, 7, f"\u2022 {line[2:]}", new_x="LMARGIN", new_y="NEXT")
                elif line:
                    pdf.multi_cell(0, 7, line)
                else:
                    pdf.ln(3)
            
            pdf.output(str(filepath))
            return {"renderer": "fpdf2_fallback"}
        except ImportError:
            # Ultimate fallback: write as text
            with open(str(filepath).replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                f.write(f"{title}\n{'='*len(title)}\n\n{content}")
            return {"renderer": "text_fallback", "note": "fpdf2 not installed, exported as .txt"}

    def _fallback_chart(self, filepath, data, chart_type):
        """Simple chart fallback using matplotlib."""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            if data:
                labels = data.get("labels", [])
                values = data.get("values", [])
                
                fig, ax = plt.subplots(figsize=(10, 6))
                fig.patch.set_facecolor('#1a1a2e')
                ax.set_facecolor('#16213e')
                
                if chart_type == "bar":
                    bars = ax.bar(labels, values, color='#00d2ff', edgecolor='#0a3d62')
                    for bar, val in zip(bars, values):
                        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                                str(val), ha='center', va='bottom', color='white', fontweight='bold')
                elif chart_type == "line":
                    ax.plot(labels, values, color='#00d2ff', linewidth=2, marker='o', 
                            markerfacecolor='#e94560', markersize=8)
                elif chart_type == "pie":
                    colors = ['#00d2ff', '#e94560', '#0a3d62', '#533483', '#16213e']
                    ax.pie(values, labels=labels, colors=colors[:len(values)], 
                           autopct='%1.1f%%', textprops={'color': 'white'})
                
                ax.tick_params(colors='white')
                ax.spines['bottom'].set_color('#333')
                ax.spines['left'].set_color('#333')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                
                plt.tight_layout()
                plt.savefig(str(filepath), dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
                plt.close()
                
                return {"renderer": "matplotlib_fallback", "chart_type": chart_type}
            
            return {"renderer": "chart", "status": "no_data"}
        except ImportError:
            print("  ⚠️ matplotlib not available.")
            return {"renderer": "chart", "status": "skipped", "reason": "matplotlib not installed"}

    def _fallback_audio(self, filepath, text):
        """Simple audio fallback using gTTS."""
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='en')
            tts.save(str(filepath))
            return {"renderer": "gtts_fallback"}
        except ImportError:
            # Save as text transcript
            txt_path = str(filepath).rsplit('.', 1)[0] + '.txt'
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"[TRANSCRIPT]\n{text}")
            return {"renderer": "text_fallback", "note": "gTTS not installed, saved as transcript"}

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    def _basic_html(self, title, content):
        """Generate basic HTML page."""
        # Convert markdown-ish content to basic HTML
        body = content.replace('\n', '<br>\n')
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ 
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background: #0f0f23; color: #e0e0e0;
            max-width: 800px; margin: 0 auto; padding: 2rem;
            line-height: 1.6;
        }}
        h1 {{ color: #00d2ff; border-bottom: 2px solid #1a1a3e; padding-bottom: 0.5rem; }}
        h2 {{ color: #a78bfa; }}
        code {{ background: #1a1a3e; padding: 2px 6px; border-radius: 4px; }}
        pre {{ background: #1a1a3e; padding: 1rem; border-radius: 8px; overflow-x: auto; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #333; padding: 8px 12px; text-align: left; }}
        th {{ background: #1a1a3e; color: #00d2ff; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    {body}
</body>
</html>"""

    def _file_size(self, filepath):
        """Get human-readable file size."""
        try:
            size = os.path.getsize(filepath)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f}{unit}"
                size /= 1024
            return f"{size:.1f}TB"
        except OSError:
            return "0B"

    # -----------------------------------------------------------------------
    # Manifest
    # -----------------------------------------------------------------------

    def manifest(self):
        """Get the manifest for this run."""
        return {
            "run_id": self.run_id,
            "created": self.created_at,
            "artifact_count": len(self.artifacts),
            "artifacts": self.artifacts
        }

    def save_manifest(self, filename="manifest.json"):
        """Save manifest to file."""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.manifest(), f, indent=2, ensure_ascii=False)
        print(f"  📋 Manifest saved: {filepath}")
        return str(filepath)

    def summary(self):
        """Print a summary of all artifacts."""
        print(f"\n{'=' * 50}")
        print(f"  Artifact Maker — Run {self.run_id}")
        print(f"{'=' * 50}")
        print(f"  Artifacts: {len(self.artifacts)}")
        print(f"  Output: {self.output_dir}")
        print()
        for a in self.artifacts:
            print(f"    📦 [{a['type'].upper():>8}] {a['filename']} ({a['size']})")
        print(f"{'=' * 50}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Artifact Maker — Multi-Format Output Engine")
    parser.add_argument("--format", required=True, 
                        choices=["markdown", "json", "yaml", "csv", "pdf", "chart", "audio", "html", "code"])
    parser.add_argument("--content", default="", help="Text content")
    parser.add_argument("--title", default="Artifact", help="Title (for PDF/HTML)")
    parser.add_argument("--output", default="artifact", help="Output filename (without extension)")
    parser.add_argument("--output-dir", default="./output", help="Output directory")

    args = parser.parse_args()

    ext_map = {
        "markdown": ".md", "json": ".json", "yaml": ".yaml", "csv": ".csv",
        "pdf": ".pdf", "chart": ".png", "audio": ".mp3", "html": ".html", "code": ".py"
    }
    
    filename = args.output + ext_map.get(args.format, ".txt")
    
    engine = ArtifactEngine(output_dir=args.output_dir)
    engine.render(args.format, filename=filename, content=args.content, title=args.title)
    engine.save_manifest()
    engine.summary()


if __name__ == "__main__":
    main()
