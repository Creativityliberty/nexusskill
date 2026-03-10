#!/usr/bin/env python3
"""
optimize_for_agent.py — Adapt a generic SKILL.md to agent-specific conventions.

Uses knowledge from 32 AI system prompts to optimize skill content for each agent's
internal processing patterns.

Usage:
    python optimize_for_agent.py --input SKILL.md --agent cursor --output optimized.md
    python optimize_for_agent.py --input SKILL.md --agent all --output-dir ./optimized/

Supported agents: claude, cursor, windsurf, cline, roo, copilot, augment, continue,
trae, gemini, universal
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


# ═══════════════════════════════════════════════════════════════
# Agent Profiles — derived from 32 AI system prompt analysis
# ═══════════════════════════════════════════════════════════════

AGENT_PROFILES = {
    "claude": {
        "name": "Claude Code",
        "dir": ".claude/skills",
        "max_lines": 500,
        "style": "reasoning",  # explain WHY
        "frontmatter": True,   # YAML frontmatter required
        "xml_tags": ["artifact_instructions", "tool_usage", "computer_use"],
        "tools": ["bash", "str_replace", "view", "create_file", "present_files",
                  "web_search", "web_fetch"],
        "priorities": ["reasoning", "examples", "references"],
        "description": "Prefers reasoning-based instructions with examples. "
                       "YAML frontmatter triggers skill loading. Under 500 lines."
    },
    "cursor": {
        "name": "Cursor",
        "dir": ".cursor/skills",
        "max_lines": 200,
        "style": "imperative",  # terse commands
        "frontmatter": False,   # .cursorrules style
        "xml_tags": [],
        "tools": ["codebase_search", "edit_file", "read_file", "grep_search",
                  "run_terminal_cmd"],
        "priorities": ["patterns", "examples", "forbidden"],
        "description": "Dense, imperative. Code examples > prose. Front-load critical info."
    },
    "windsurf": {
        "name": "Windsurf",
        "dir": ".windsurf/skills",
        "max_lines": 400,
        "style": "workflow",  # step-by-step
        "frontmatter": False,
        "xml_tags": ["flow"],
        "tools": ["create_file", "edit_file", "read_file", "run_command",
                  "search", "browser", "deploy"],
        "priorities": ["steps", "examples", "verification"],
        "description": "Workflow-oriented with numbered steps. Cascade execution model."
    },
    "cline": {
        "name": "Cline",
        "dir": ".cline/skills",
        "max_lines": 400,
        "style": "procedural",  # tool-use oriented
        "frontmatter": False,
        "xml_tags": ["ask_followup_question", "attempt_completion",
                     "environment_details", "read_file", "write_to_file"],
        "tools": ["read_file", "write_to_file", "replace_in_file",
                  "search_files", "execute_command", "browser_action"],
        "priorities": ["tool_examples", "decision_tree", "verification"],
        "description": "Tool-use oriented with decision trees. Show tool call examples."
    },
    "roo": {
        "name": "Roo Code",
        "dir": ".roo/skills",
        "max_lines": 400,
        "style": "procedural",
        "frontmatter": False,
        "xml_tags": ["ask_followup_question", "attempt_completion"],
        "tools": ["read_file", "write_to_file", "replace_in_file",
                  "search_files", "execute_command"],
        "priorities": ["tool_examples", "decision_tree", "modes"],
        "description": "Similar to Cline with mode system (Code, Architect, Ask, Debug)."
    },
    "copilot": {
        "name": "GitHub Copilot",
        "dir": ".agents/skills",
        "max_lines": 300,
        "style": "examples",  # pattern-based
        "frontmatter": False,
        "xml_tags": [],
        "tools": [],
        "priorities": ["code_examples", "patterns", "signatures"],
        "description": "Example-heavy, pattern-based. Show input→output transformations."
    },
    "augment": {
        "name": "Augment",
        "dir": ".augment/skills",
        "max_lines": 400,
        "style": "contextual",  # multi-file aware
        "frontmatter": False,
        "xml_tags": ["augment_code_snippet"],
        "tools": ["codebase_search", "file_read", "file_write",
                  "file_str_replace", "shell_exec"],
        "priorities": ["architecture", "dependencies", "cross_file"],
        "description": "Context-rich. Include dependency graphs and file relationships."
    },
    "continue": {
        "name": "Continue",
        "dir": ".continue/skills",
        "max_lines": 400,
        "style": "flexible",
        "frontmatter": False,
        "xml_tags": [],
        "tools": [],
        "priorities": ["configuration", "examples", "backends"],
        "description": "Open-source, model-agnostic. Include config examples."
    },
    "trae": {
        "name": "Trae",
        "dir": ".trae/skills",
        "max_lines": 400,
        "style": "structured",
        "frontmatter": False,
        "xml_tags": [],
        "tools": ["file_read", "file_write", "edit_file", "run_command",
                  "search", "browser_navigate"],
        "priorities": ["headings", "steps", "verification"],
        "description": "Well-structured with clear heading hierarchy."
    },
    "universal": {
        "name": "Universal (Gemini CLI, OpenCode, Amp, Codex, Kimi CLI)",
        "dir": ".agents/skills",
        "max_lines": 400,
        "style": "clean",
        "frontmatter": True,
        "xml_tags": [],
        "tools": [],
        "priorities": ["clarity", "examples", "portability"],
        "description": "Clean standard markdown. No agent-specific conventions."
    }
}


# ═══════════════════════════════════════════════════════════════
# Optimization Functions
# ═══════════════════════════════════════════════════════════════

def parse_skill(content: str) -> dict:
    """Parse a SKILL.md into frontmatter + sections."""
    result = {"frontmatter": "", "sections": [], "raw": content}

    # Extract YAML frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if fm_match:
        result["frontmatter"] = fm_match.group(1)
        content = content[fm_match.end():]

    # Extract sections by H2
    sections = re.split(r'\n(?=## )', content)
    for section in sections:
        title_match = re.match(r'^## (.+)\n', section)
        if title_match:
            result["sections"].append({
                "title": title_match.group(1).strip(),
                "content": section
            })
        elif section.strip():
            result["sections"].insert(0, {
                "title": "_intro",
                "content": section
            })

    return result


def optimize_for_claude(parsed: dict) -> str:
    """Optimize for Claude Code — reasoning-based with frontmatter."""
    lines = []

    # Ensure YAML frontmatter exists
    if parsed["frontmatter"]:
        lines.append(f"---\n{parsed['frontmatter']}\n---\n")

    # Reorder: intro → quick ref → examples → detailed → troubleshooting
    priority_order = ["_intro", "Quick Reference", "Examples",
                      "Core Guide", "Detailed Guide", "API",
                      "Troubleshooting", "Configuration"]

    used = set()
    for target in priority_order:
        for section in parsed["sections"]:
            if section["title"].lower().startswith(target.lower()):
                lines.append(section["content"])
                used.add(section["title"])

    # Append remaining sections
    for section in parsed["sections"]:
        if section["title"] not in used:
            lines.append(section["content"])

    result = "\n".join(lines)

    # Enforce 500 line limit
    result_lines = result.split("\n")
    if len(result_lines) > 500:
        result = "\n".join(result_lines[:490])
        result += "\n\n---\n*See references/ directory for complete documentation.*\n"

    return result


def optimize_for_cursor(parsed: dict) -> str:
    """Optimize for Cursor — dense, imperative, code-heavy."""
    lines = []

    # No YAML frontmatter for .cursorrules style
    # Start with the most critical patterns

    for section in parsed["sections"]:
        content = section["content"]

        # Remove verbose explanations, keep code blocks and imperatives
        # Shorten paragraphs to key points
        paragraphs = content.split("\n\n")
        condensed = []
        for para in paragraphs:
            if para.strip().startswith("```"):
                condensed.append(para)  # keep all code blocks
            elif para.strip().startswith("- ") or para.strip().startswith("| "):
                condensed.append(para)  # keep lists and tables
            elif para.strip().startswith("#"):
                condensed.append(para)  # keep headings
            else:
                # Condense prose to first sentence
                sentences = para.split(". ")
                if sentences:
                    first = sentences[0].strip()
                    if first and len(first) > 10:
                        condensed.append(first + ".")

        lines.append("\n\n".join(condensed))

    result = "\n".join(lines)

    # Enforce 200 line limit
    result_lines = result.split("\n")
    if len(result_lines) > 200:
        result = "\n".join(result_lines[:195])
        result += "\n\n<!-- Full docs: .agents/skills/{name}/SKILL.md -->\n"

    return result


def optimize_for_windsurf(parsed: dict) -> str:
    """Optimize for Windsurf — workflow steps with verification."""
    lines = []

    for section in parsed["sections"]:
        content = section["content"]

        # Convert prose instructions into numbered steps where possible
        paragraphs = content.split("\n\n")
        step_count = 0
        converted = []

        for para in paragraphs:
            if para.strip().startswith("#") or para.strip().startswith("```"):
                converted.append(para)
            elif para.strip().startswith("- "):
                # Convert bullet lists to numbered steps if they look like instructions
                bullet_lines = para.strip().split("\n")
                is_instruction = any(line.strip().startswith("- ") and
                                     any(v in line.lower() for v in
                                         ["run", "create", "add", "set", "configure",
                                          "install", "open", "check", "verify"])
                                     for line in bullet_lines)
                if is_instruction:
                    for line in bullet_lines:
                        if line.strip().startswith("- "):
                            step_count += 1
                            converted.append(f"**Step {step_count}:** {line.strip()[2:]}")
                else:
                    converted.append(para)
            else:
                converted.append(para)

        lines.append("\n\n".join(converted))

    return "\n".join(lines)


def optimize_for_cline(parsed: dict) -> str:
    """Optimize for Cline/Roo — tool-use oriented with decision trees."""
    lines = []

    for section in parsed["sections"]:
        content = section["content"]
        lines.append(content)

    # Add tool usage hints at the end
    lines.append("\n\n## Tool Usage Hints\n")
    lines.append("When working with this library:\n")
    lines.append("- Use `read_file` to check existing configuration before making changes")
    lines.append("- Use `search_files` to find usage patterns in the codebase")
    lines.append("- Use `execute_command` for installation and build commands")
    lines.append("- Use `replace_in_file` for targeted code modifications")
    lines.append("- Always verify changes with `execute_command` (run tests/linter)")

    return "\n".join(lines)


def optimize_for_copilot(parsed: dict) -> str:
    """Optimize for Copilot — example-heavy, pattern-based."""
    lines = []

    # Prioritize sections with code examples
    code_sections = []
    other_sections = []

    for section in parsed["sections"]:
        if "```" in section["content"]:
            code_sections.append(section)
        else:
            other_sections.append(section)

    # Code-heavy sections first
    for section in code_sections:
        lines.append(section["content"])

    for section in other_sections:
        lines.append(section["content"])

    return "\n".join(lines)


def optimize_generic(parsed: dict) -> str:
    """Generic optimization — clean, portable markdown."""
    lines = []

    if parsed["frontmatter"]:
        lines.append(f"---\n{parsed['frontmatter']}\n---\n")

    for section in parsed["sections"]:
        lines.append(section["content"])

    return "\n".join(lines)


# Optimization dispatch
OPTIMIZERS = {
    "claude": optimize_for_claude,
    "cursor": optimize_for_cursor,
    "windsurf": optimize_for_windsurf,
    "cline": optimize_for_cline,
    "roo": optimize_for_cline,  # same base as Cline
    "copilot": optimize_for_copilot,
    "augment": optimize_generic,
    "continue": optimize_generic,
    "trae": optimize_generic,
    "universal": optimize_generic,
}


def optimize(content: str, agent: str) -> str:
    """Main optimization entry point."""
    if agent not in OPTIMIZERS:
        print(f"Warning: unknown agent '{agent}', using generic optimization")
        agent = "universal"

    parsed = parse_skill(content)
    optimizer = OPTIMIZERS[agent]
    result = optimizer(parsed)

    profile = AGENT_PROFILES[agent]
    max_lines = profile["max_lines"]
    result_lines = result.split("\n")
    if len(result_lines) > max_lines:
        result = "\n".join(result_lines[:max_lines - 5])
        result += f"\n\n---\n*Truncated to {max_lines} lines for {profile['name']}.*\n"

    return result


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Adapt SKILL.md to agent-specific conventions"
    )
    parser.add_argument('--input', '-i', type=Path, required=True,
                        help='Input SKILL.md file')
    parser.add_argument('--agent', '-a', type=str, required=True,
                        help='Target agent (claude, cursor, windsurf, cline, roo, '
                             'copilot, augment, continue, trae, universal, all)')
    parser.add_argument('--output', '-o', type=Path,
                        help='Output file (for single agent)')
    parser.add_argument('--output-dir', type=Path,
                        help='Output directory (for --agent all)')
    parser.add_argument('--list-agents', action='store_true',
                        help='List all supported agents')

    args = parser.parse_args()

    if args.list_agents:
        print("Supported agents:")
        for key, profile in AGENT_PROFILES.items():
            print(f"  {key:12s} → {profile['name']} ({profile['dir']})")
        return

    content = args.input.read_text(encoding='utf-8')

    if args.agent == "all":
        output_dir = args.output_dir or Path("./optimized")
        output_dir.mkdir(parents=True, exist_ok=True)

        for agent_key in OPTIMIZERS:
            result = optimize(content, agent_key)
            out_path = output_dir / f"SKILL.{agent_key}.md"
            out_path.write_text(result, encoding='utf-8')
            lines = len(result.split("\n"))
            print(f"✓ {agent_key:12s} → {out_path} ({lines} lines)")

    else:
        result = optimize(content, args.agent)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(result, encoding='utf-8')
            lines = len(result.split("\n"))
            print(f"✓ {args.agent} → {args.output} ({lines} lines)")
        else:
            print(result)


if __name__ == '__main__':
    main()
