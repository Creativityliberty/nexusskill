"""
Chart Renderer
===============
Generates charts and diagrams as PNG/SVG images.
Uses matplotlib for data charts and can output Mermaid code for diagrams.

Install: pip install matplotlib
"""

from pathlib import Path


class ChartRenderer:
    """Renders charts and visual diagrams."""

    def render(self, filepath, data=None, chart_type="bar", title="Chart",
               mermaid_code=None, colors=None, **kwargs):
        """
        Generate a chart image.
        
        Args:
            filepath: Output path (.png or .svg)
            data: Dict with "labels" and "values" (and optionally "series")
            chart_type: bar, line, pie, horizontal_bar, scatter
            title: Chart title
            mermaid_code: If provided, saves Mermaid code to .mmd file instead
            colors: Custom color palette
        """
        if mermaid_code:
            return self._render_mermaid(filepath, mermaid_code)
        
        if not data:
            return {"renderer": "chart", "status": "no_data"}

        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import matplotlib.font_manager as fm
        except ImportError:
            raise ImportError("Install matplotlib: pip install matplotlib")

        labels = data.get("labels", [])
        values = data.get("values", [])
        
        # Premium dark theme
        palette = colors or ['#00d2ff', '#e94560', '#533483', '#0a3d62', '#a78bfa', 
                             '#22c55e', '#f97316', '#ec4899']

        fig, ax = plt.subplots(figsize=(12, 7))
        fig.patch.set_facecolor('#0f0f23')
        ax.set_facecolor('#1a1a2e')
        
        if chart_type == "bar":
            bars = ax.bar(labels, values, color=palette[:len(values)], 
                         edgecolor='#333', linewidth=0.5, width=0.6)
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(values)*0.02,
                        str(val), ha='center', va='bottom', color='white', fontweight='bold', fontsize=11)
        
        elif chart_type == "horizontal_bar":
            bars = ax.barh(labels, values, color=palette[:len(values)], 
                          edgecolor='#333', linewidth=0.5, height=0.6)
            for bar, val in zip(bars, values):
                ax.text(val + max(values)*0.02, bar.get_y() + bar.get_height()/2.,
                        str(val), ha='left', va='center', color='white', fontweight='bold', fontsize=11)

        elif chart_type == "line":
            ax.plot(labels, values, color='#00d2ff', linewidth=2.5, marker='o',
                    markerfacecolor='#e94560', markersize=10, markeredgecolor='white', markeredgewidth=1.5)
            ax.fill_between(range(len(values)), values, alpha=0.15, color='#00d2ff')
        
        elif chart_type == "pie":
            wedges, texts, autotexts = ax.pie(
                values, labels=labels, colors=palette[:len(values)],
                autopct='%1.1f%%', textprops={'color': 'white', 'fontsize': 11},
                wedgeprops={'edgecolor': '#0f0f23', 'linewidth': 2},
                pctdistance=0.75
            )
            for t in autotexts:
                t.set_fontweight('bold')
        
        elif chart_type == "scatter":
            x_vals = data.get("x", list(range(len(values))))
            ax.scatter(x_vals, values, c=palette[0], s=100, alpha=0.8, edgecolors='white', linewidth=1)

        # Styling
        ax.set_title(title, color='white', fontsize=16, fontweight='bold', pad=15)
        ax.tick_params(colors='#aaa', labelsize=10)
        
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        for spine in ['bottom', 'left']:
            ax.spines[spine].set_color('#333')
        
        ax.grid(axis='y', alpha=0.2, color='#444')
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close()
        
        return {"renderer": "chart_renderer", "chart_type": chart_type, "data_points": len(values)}

    def _render_mermaid(self, filepath, mermaid_code):
        """Save Mermaid code to a .mmd file for external rendering."""
        mmd_path = Path(filepath).with_suffix('.mmd')
        with open(mmd_path, 'w', encoding='utf-8') as f:
            f.write(mermaid_code)
        
        # Also save an HTML with embedded Mermaid
        html_path = Path(filepath).with_suffix('.html')
        html = f"""<!DOCTYPE html>
<html><head>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<style>body {{ background: #0f0f23; display: flex; justify-content: center; padding: 2rem; }}</style>
</head><body>
<pre class="mermaid">{mermaid_code}</pre>
<script>mermaid.initialize({{ theme: 'dark' }});</script>
</body></html>"""
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return {"renderer": "mermaid", "mmd_file": str(mmd_path), "html_file": str(html_path)}
