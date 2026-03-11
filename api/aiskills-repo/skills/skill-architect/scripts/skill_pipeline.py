#!/usr/bin/env python3
"""
Skill Architect Pipeline — Data Models & CLI
============================================
Blueprint of the multi-agent pipeline used by the skill-architect skill.
Claude plays all agent roles; this script handles I/O and data structures.

Usage:
    python skill_pipeline.py <skill-folder>
    python skill_pipeline.py skills/my-skill/
"""

from __future__ import annotations
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import TypedDict

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class SkillData(TypedDict):
    name: str
    description: str
    content: str        # Full SKILL.md content
    scripts: dict[str, str]     # {filename: content}
    references: dict[str, str]  # {filename: content}
    assets: list[str]           # filenames only


class SkillArchitecture(TypedDict):
    components: list[str]
    dependencies: dict[str, list[str]]
    concerns: list[str]
    line_count: int


class CodeRefactoringPlan(TypedDict):
    scripts_to_modify: dict[str, str]   # {path: instructions}
    skill_md_updates: str | None


class ReviewFeedback(TypedDict):
    suggestions: list[str]
    positives: list[str]
    priority: str   # "High" | "Medium" | "Low"


class SecurityAuditReport(TypedDict):
    vulnerabilities: list[str]
    recommendations: list[str]
    severity: str   # "Critical" | "High" | "Medium" | "Low" | "Clean"


class EnhancedDocumentation(TypedDict):
    description_improvements: str
    examples: list[str]
    usage_instructions: str
    wrap_up_section: str


class PipelineReport(TypedDict):
    skill: str
    architecture: SkillArchitecture
    refactoring: CodeRefactoringPlan
    review: ReviewFeedback
    security: SecurityAuditReport
    documentation: EnhancedDocumentation


# ---------------------------------------------------------------------------
# Skill loader
# ---------------------------------------------------------------------------

def load_skill(skill_path: Path) -> SkillData:
    """Load all files from a skill folder into a SkillData dict."""
    if not skill_path.is_dir():
        raise FileNotFoundError(f"Skill folder not found: {skill_path}")

    skill_md_path = skill_path / "SKILL.md"
    if not skill_md_path.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_path}")

    content = skill_md_path.read_text(encoding="utf-8")

    # Extract name from frontmatter
    name = skill_path.name
    description = ""
    for line in content.splitlines():
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip()
        if line.startswith("description:"):
            description = line.split(":", 1)[1].strip()

    # Load scripts
    scripts: dict[str, str] = {}
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        for f in sorted(scripts_dir.iterdir()):
            if f.is_file():
                scripts[f.name] = f.read_text(encoding="utf-8")

    # Load references
    references: dict[str, str] = {}
    refs_dir = skill_path / "references"
    if refs_dir.exists():
        for f in sorted(refs_dir.iterdir()):
            if f.is_file():
                references[f.name] = f.read_text(encoding="utf-8")

    # List assets
    assets: list[str] = []
    assets_dir = skill_path / "assets"
    if assets_dir.exists():
        assets = [f.name for f in sorted(assets_dir.iterdir()) if f.is_file()]

    return SkillData(
        name=name,
        description=description,
        content=content,
        scripts=scripts,
        references=references,
        assets=assets,
    )


# ---------------------------------------------------------------------------
# Static analysis helpers (run before Claude's agent roles)
# ---------------------------------------------------------------------------

def static_architecture_check(skill: SkillData) -> SkillArchitecture:
    """Quick static checks — Claude then provides the full analysis."""
    components = ["SKILL.md"]
    dependencies: dict[str, list[str]] = {}
    concerns: list[str] = []

    content = skill["content"]
    line_count = len(content.splitlines())

    if skill["scripts"]:
        components.append("scripts/")
    if skill["references"]:
        components.append("references/")
        # Mark which references are linked from SKILL.md
        linked = [r for r in skill["references"] if r in content]
        unlinked = [r for r in skill["references"] if r not in content]
        if linked:
            dependencies["SKILL.md"] = linked
        if unlinked:
            concerns.append(f"Unlinked references: {unlinked}")
    if skill["assets"]:
        components.append("assets/")

    if line_count > 500:
        concerns.append(f"SKILL.md is {line_count} lines (>500 limit, move content to references/)")

    # Check for extraneous files
    bad_files = [f for f in ["README.md", "CHANGELOG.md", "INSTALLATION.md"] if f in content]
    if bad_files:
        concerns.append(f"Extraneous docs detected: {bad_files}")

    return SkillArchitecture(
        components=components,
        dependencies=dependencies,
        concerns=concerns,
        line_count=line_count,
    )


def static_security_check(skill: SkillData) -> list[str]:
    """Quick pattern-based security scan across all files."""
    findings: list[str] = []
    all_files = {"SKILL.md": skill["content"], **skill["scripts"], **skill["references"]}

    patterns = {
        r"input()": "Python input() without sanitization",
        r"eval(": "eval() call — potential code injection",
        r"shell=True": "subprocess shell=True — risk of shell injection",
        r"verify=False": "TLS verification disabled",
        r"chmod 777": "Overly permissive chmod 777",
        r"API_KEY": "Possible hardcoded API key reference",
        r"password": "Possible hardcoded password",
    }

    for filename, file_content in all_files.items():
        for pattern, description in patterns.items():
            if pattern in file_content:
                findings.append(f"{filename}: {description}")

    return findings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Skill Architect — static analysis pre-pass before Claude's multi-agent review"
    )
    parser.add_argument("skill_path", type=Path, help="Path to the skill folder")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    try:
        skill = load_skill(args.skill_path)
    except FileNotFoundError as e:
        log.error(str(e))
        sys.exit(1)

    arch = static_architecture_check(skill)
    sec_findings = static_security_check(skill)

    report = {
        "skill": skill["name"],
        "line_count": arch["line_count"],
        "components": arch["components"],
        "dependencies": arch["dependencies"],
        "concerns": arch["concerns"],
        "security_findings": sec_findings,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  Skill Architect — Pre-Analysis: {skill['name']}")
        print(f"{'='*60}\n")
        print(f"Components: {', '.join(arch['components'])}")
        print(f"SKILL.md: {arch['line_count']} lines")

        if arch["concerns"]:
            print("\n⚠️  Structural concerns:")
            for c in arch["concerns"]:
                print(f"   - {c}")

        if sec_findings:
            print("\n🔒 Security findings:")
            for f in sec_findings:
                print(f"   - {f}")
        else:
            print("\n🔒 Security: No obvious issues detected")

        print(f"\n→ Pass this output to Claude with: 'Run the skill-architect pipeline on {args.skill_path}'")
        print()


if __name__ == "__main__":
    main()
