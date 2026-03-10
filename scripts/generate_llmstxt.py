#!/usr/bin/env python3
"""
generate_llmstxt.py — Generate llms.txt and SKILL.md from project documentation.

Usage:
    python generate_llmstxt.py --source ./docs --output ./llms.txt [--full] [--skill]
    python generate_llmstxt.py --readme ./README.md --name "My Project" --output ./llms.txt

Reads documentation from various sources and generates:
- llms.txt: Concise index of documentation with links
- llms-full.txt: Complete documentation content (with --full)
- SKILL.md: AI agent skill file (with --skill)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def extract_title_from_markdown(content: str) -> str:
    """Extract the first H1 heading from markdown content."""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return match.group(1).strip() if match else "Untitled"


def extract_summary_from_markdown(content: str) -> str:
    """Extract a summary — first paragraph after the title."""
    lines = content.split('\n')
    in_content = False
    summary_lines = []

    for line in lines:
        if line.startswith('# ') and not in_content:
            in_content = True
            continue
        if in_content:
            if line.strip() == '' and summary_lines:
                break
            if line.strip() and not line.startswith('#'):
                summary_lines.append(line.strip())

    return ' '.join(summary_lines)[:300] if summary_lines else ""


def extract_headings(content: str) -> list[dict]:
    """Extract all headings with their level and content."""
    headings = []
    for match in re.finditer(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE):
        headings.append({
            'level': len(match.group(1)),
            'text': match.group(2).strip(),
            'position': match.start()
        })
    return headings


def scan_docs_directory(docs_path: Path) -> list[dict]:
    """Scan a docs directory and return a list of documentation files."""
    doc_files = []
    extensions = {'.md', '.mdx', '.txt', '.rst'}

    for file_path in sorted(docs_path.rglob('*')):
        if file_path.suffix.lower() in extensions and file_path.is_file():
            rel_path = file_path.relative_to(docs_path)
            content = file_path.read_text(encoding='utf-8', errors='replace')
            title = extract_title_from_markdown(content)
            summary = extract_summary_from_markdown(content)

            doc_files.append({
                'path': str(rel_path),
                'title': title,
                'summary': summary,
                'content': content,
                'size': len(content)
            })

    return doc_files


def scan_readme(readme_path: Path) -> dict:
    """Scan a README file and extract structured info."""
    content = readme_path.read_text(encoding='utf-8', errors='replace')
    return {
        'title': extract_title_from_markdown(content),
        'summary': extract_summary_from_markdown(content),
        'content': content,
        'headings': extract_headings(content)
    }


def scan_openapi(spec_path: Path) -> Optional[dict]:
    """Scan an OpenAPI spec and extract API info."""
    try:
        content = spec_path.read_text(encoding='utf-8')
        if spec_path.suffix in ('.json',):
            spec = json.loads(content)
        else:
            try:
                import yaml
                spec = yaml.safe_load(content)
            except ImportError:
                return None

        info = spec.get('info', {})
        paths = spec.get('paths', {})

        endpoints = []
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH'):
                    endpoints.append({
                        'method': method.upper(),
                        'path': path,
                        'summary': details.get('summary', ''),
                        'description': details.get('description', '')[:200]
                    })

        return {
            'title': info.get('title', 'API'),
            'version': info.get('version', ''),
            'description': info.get('description', ''),
            'endpoints': endpoints
        }
    except Exception:
        return None


def generate_llmstxt(
    project_name: str,
    project_summary: str,
    doc_files: list[dict],
    base_url: str = "",
    api_info: Optional[dict] = None
) -> str:
    """Generate the llms.txt content (concise index version)."""
    lines = [f"# {project_name}", ""]

    if project_summary:
        lines.append(f"> {project_summary}")
        lines.append("")

    # Group docs by directory / section
    sections: dict[str, list] = {}
    for doc in doc_files:
        parts = Path(doc['path']).parts
        section = parts[0] if len(parts) > 1 else "Docs"
        section = section.replace('-', ' ').replace('_', ' ').title()
        sections.setdefault(section, []).append(doc)

    for section_name, docs in sections.items():
        lines.append(f"## {section_name}")
        lines.append("")
        for doc in docs:
            url = f"{base_url}/{doc['path']}" if base_url else doc['path']
            summary = doc['summary'][:100] + "..." if len(doc['summary']) > 100 else doc['summary']
            lines.append(f"- [{doc['title']}]({url}): {summary}")
        lines.append("")

    if api_info:
        lines.append("## API Reference")
        lines.append("")
        lines.append(f"{api_info['title']} v{api_info['version']}")
        lines.append("")
        for endpoint in api_info['endpoints'][:20]:
            desc = endpoint['summary'] or endpoint['description'][:80]
            lines.append(f"- `{endpoint['method']} {endpoint['path']}`: {desc}")
        lines.append("")

    return '\n'.join(lines)


def generate_llmstxt_full(
    project_name: str,
    project_summary: str,
    doc_files: list[dict],
    api_info: Optional[dict] = None,
    max_size_kb: int = 500
) -> str:
    """Generate the llms-full.txt content (complete documentation)."""
    lines = [f"# {project_name}", ""]

    if project_summary:
        lines.append(f"> {project_summary}")
        lines.append("")

    current_size = 0
    max_size = max_size_kb * 1024

    for doc in doc_files:
        if current_size + len(doc['content']) > max_size:
            lines.append(f"\n---\n*Truncated: remaining {len(doc_files)} files omitted to stay within size limit.*\n")
            break

        lines.append(f"\n---\n")
        lines.append(doc['content'])
        current_size += len(doc['content'])

    if api_info:
        lines.append("\n---\n## API Reference\n")
        for endpoint in api_info['endpoints']:
            lines.append(f"### `{endpoint['method']} {endpoint['path']}`\n")
            if endpoint['summary']:
                lines.append(f"{endpoint['summary']}\n")
            if endpoint['description']:
                lines.append(f"{endpoint['description']}\n")

    return '\n'.join(lines)


def generate_skill_md(
    project_name: str,
    project_slug: str,
    project_summary: str,
    doc_files: list[dict],
    api_info: Optional[dict] = None
) -> str:
    """Generate a SKILL.md file for AI agent consumption."""

    # Build a comprehensive but concise skill description
    keywords = set()
    for doc in doc_files:
        words = re.findall(r'\b[a-zA-Z]{3,}\b', doc['title'].lower())
        keywords.update(words[:5])

    trigger_contexts = ", ".join(sorted(keywords)[:15])

    lines = [
        "---",
        f"name: {project_slug}",
        "description: >",
        f"  Documentation and usage guide for {project_name}. Use this skill whenever",
        f"  working with {project_name}, its APIs, configuration, or integration.",
        f"  Trigger on mentions of: {trigger_contexts}.",
        f"  Also trigger when debugging issues, writing code, or building features",
        f"  that involve {project_name}.",
        "---",
        "",
        f"# {project_name}",
        "",
    ]

    if project_summary:
        lines.append(f"{project_summary}")
        lines.append("")

    # Quick reference — first doc or README content (truncated)
    lines.append("## Quick Reference")
    lines.append("")

    if doc_files:
        first_doc = doc_files[0]
        # Take first 50 lines of first doc
        quick_ref = '\n'.join(first_doc['content'].split('\n')[:50])
        lines.append(quick_ref)
        lines.append("")

    # Key topics from other docs
    if len(doc_files) > 1:
        lines.append("## Topics Covered")
        lines.append("")
        for doc in doc_files[1:10]:
            lines.append(f"### {doc['title']}")
            lines.append("")
            # First 10 lines of each
            excerpt = '\n'.join(doc['content'].split('\n')[:10])
            lines.append(excerpt)
            lines.append("")

    if api_info:
        lines.append("## API Endpoints")
        lines.append("")
        for endpoint in api_info['endpoints'][:15]:
            lines.append(f"### `{endpoint['method']} {endpoint['path']}`")
            if endpoint['summary']:
                lines.append(f"{endpoint['summary']}")
            lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate llms.txt, llms-full.txt, and SKILL.md from project docs"
    )
    parser.add_argument('--source', '-s', type=Path, help='Documentation source directory')
    parser.add_argument('--readme', type=Path, help='README file path')
    parser.add_argument('--openapi', type=Path, help='OpenAPI spec file (JSON or YAML)')
    parser.add_argument('--name', '-n', type=str, help='Project name (auto-detected if not set)')
    parser.add_argument('--url', type=str, default='', help='Base URL for documentation links')
    parser.add_argument('--output', '-o', type=Path, default=Path('.'), help='Output directory')
    parser.add_argument('--full', action='store_true', help='Also generate llms-full.txt')
    parser.add_argument('--skill', action='store_true', help='Also generate SKILL.md')
    parser.add_argument('--max-size', type=int, default=500, help='Max size for full version (KB)')

    args = parser.parse_args()

    # Collect documentation
    doc_files = []
    project_name = args.name or "My Project"
    project_summary = ""

    if args.readme:
        readme_info = scan_readme(args.readme)
        project_name = args.name or readme_info['title']
        project_summary = readme_info['summary']
        doc_files.append({
            'path': str(args.readme.name),
            'title': readme_info['title'],
            'summary': readme_info['summary'],
            'content': readme_info['content'],
            'size': len(readme_info['content'])
        })

    if args.source and args.source.is_dir():
        source_docs = scan_docs_directory(args.source)
        doc_files.extend(source_docs)
        if not project_summary and source_docs:
            project_summary = source_docs[0]['summary']
        if not args.name and source_docs:
            project_name = source_docs[0]['title']

    api_info = None
    if args.openapi and args.openapi.is_file():
        api_info = scan_openapi(args.openapi)

    if not doc_files and not api_info:
        print("Error: No documentation sources found. Use --source, --readme, or --openapi.")
        sys.exit(1)

    # Generate outputs
    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    # llms.txt
    llms_txt = generate_llmstxt(project_name, project_summary, doc_files, args.url, api_info)
    llms_path = output_dir / 'llms.txt'
    llms_path.write_text(llms_txt, encoding='utf-8')
    print(f"✓ Generated {llms_path} ({len(llms_txt)} bytes)")

    # llms-full.txt
    if args.full:
        llms_full = generate_llmstxt_full(
            project_name, project_summary, doc_files, api_info, args.max_size
        )
        full_path = output_dir / 'llms-full.txt'
        full_path.write_text(llms_full, encoding='utf-8')
        print(f"✓ Generated {full_path} ({len(llms_full)} bytes)")

    # SKILL.md
    if args.skill:
        project_slug = slugify(project_name)
        skill_md = generate_skill_md(
            project_name, project_slug, project_summary, doc_files, api_info
        )
        skill_path = output_dir / 'SKILL.md'
        skill_path.write_text(skill_md, encoding='utf-8')
        print(f"✓ Generated {skill_path} ({len(skill_md)} bytes)")


if __name__ == '__main__':
    main()
