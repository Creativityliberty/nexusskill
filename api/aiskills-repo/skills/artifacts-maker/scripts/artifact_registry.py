#!/usr/bin/env python3
"""
Artifacts Maker — Registry & Manifest Manager
==============================================
Tracks all outputs produced by a workflow as structured artifacts.

Commands:
  init      Create artifacts/ dir + empty manifest.json
  add       Register a new artifact
  list      List all artifacts (optionally filtered by type)
  validate  Validate an artifact against its type schema
  report    Generate a Markdown summary report

Usage:
  python artifact_registry.py init
  python artifact_registry.py add --file out.md --type markdown --task-id t1 --skill ui-style-generator
  python artifact_registry.py list [--type markdown]
  python artifact_registry.py validate --file out.json --type design-system
  python artifact_registry.py report [--output report.md]
"""

from __future__ import annotations
import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

ArtifactType = Literal[
    "markdown", "code", "design-system", "config",
    "report", "commit", "diff", "image", "text", "unknown"
]

EXT_TO_TYPE: dict[str, ArtifactType] = {
    ".md": "markdown",
    ".py": "code", ".ts": "code", ".js": "code", ".sh": "code", ".tsx": "code",
    ".json": "config",
    ".yaml": "config", ".yml": "config", ".toml": "config",
    ".patch": "diff", ".diff": "diff",
    ".png": "image", ".jpg": "image", ".jpeg": "image", ".svg": "image",
    ".txt": "text",
}

ARTIFACTS_DIR = Path("artifacts")
MANIFEST_FILE = ARTIFACTS_DIR / "manifest.json"


# ---------------------------------------------------------------------------
# Manifest I/O
# ---------------------------------------------------------------------------

def load_manifest() -> list[dict]:
    if not MANIFEST_FILE.exists():
        return []
    return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))


def save_manifest(entries: list[dict]) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_FILE.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_init() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    if not MANIFEST_FILE.exists():
        save_manifest([])
        print(f"✅ Initialized: {ARTIFACTS_DIR}/ + {MANIFEST_FILE}")
    else:
        print(f"ℹ️  Already initialized: {ARTIFACTS_DIR}/")


def cmd_add(
    file: Path,
    artifact_type: Optional[ArtifactType],
    task_id: str,
    skill: str,
    description: str,
) -> None:
    if not file.exists():
        print(f"❌ File not found: {file}", file=sys.stderr)
        sys.exit(1)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    # Auto-detect type if not provided
    if not artifact_type:
        artifact_type = EXT_TO_TYPE.get(file.suffix.lower(), "unknown")

    # Assign sequence number
    entries = load_manifest()
    seq = len(entries) + 1
    dest_name = f"{seq:03d}_{file.name}"
    dest_path = ARTIFACTS_DIR / dest_name

    # Copy file
    shutil.copy2(file, dest_path)

    # Build entry
    entry = {
        "id": f"{seq:03d}",
        "seq": seq,
        "name": file.name,
        "stored_as": dest_name,
        "type": artifact_type,
        "source_task": task_id,
        "source_skill": skill,
        "description": description,
        "path": str(dest_path),
        "size_bytes": dest_path.stat().st_size,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    entries.append(entry)
    save_manifest(entries)

    print(f"✅ Artifact registered: [{entry['id']}] {dest_name} ({artifact_type}, {entry['size_bytes']} bytes)")


def cmd_list(artifact_type: Optional[str]) -> None:
    entries = load_manifest()
    if not entries:
        print("No artifacts yet. Run: artifact_registry.py init")
        return

    if artifact_type:
        entries = [e for e in entries if e.get("type") == artifact_type]

    if not entries:
        print(f"No artifacts of type '{artifact_type}'")
        return

    # Table
    print(f"\n{'ID':<5} {'Name':<35} {'Type':<15} {'Skill':<25} {'Size':>8}")
    print("-" * 92)
    for e in entries:
        size = f"{e['size_bytes']:,}B"
        print(f"{e['id']:<5} {e['name']:<35} {e['type']:<15} {e['source_skill']:<25} {size:>8}")
    print(f"\nTotal: {len(entries)} artifact(s)")


def cmd_validate(file: Path, artifact_type: str) -> None:
    """Basic validation per type. Extend with Pydantic for production use."""
    if not file.exists():
        print(f"❌ File not found: {file}", file=sys.stderr)
        sys.exit(1)

    content = file.read_text(encoding="utf-8") if file.suffix not in {".png", ".jpg"} else ""
    size = file.stat().st_size

    errors: list[str] = []

    if size == 0:
        errors.append("File is empty")

    if artifact_type == "design-system":
        try:
            data = json.loads(content)
            required = ["projectName", "colors", "typography", "spacing"]
            missing = [k for k in required if k not in data]
            if missing:
                errors.append(f"Missing required fields: {missing}")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {e}")

    elif artifact_type == "config":
        try:
            json.loads(content)
        except json.JSONDecodeError:
            try:
                import tomllib  # type: ignore
                tomllib.loads(content)
            except Exception:
                pass  # YAML validation would need pyyaml

    elif artifact_type == "markdown":
        if not any(line.startswith("#") for line in content.splitlines()):
            errors.append("No headings found (expected at least one # heading)")

    elif artifact_type == "diff":
        if not content.startswith("---") and "@@" not in content:
            errors.append("Does not look like a valid diff/patch")

    if errors:
        print(f"❌ Validation failed for {file.name}:")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)
    else:
        print(f"✅ Valid {artifact_type}: {file.name}")


def cmd_report(output: Optional[Path]) -> None:
    entries = load_manifest()

    lines = [
        "# Artifacts Report",
        f"\nGenerated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Total artifacts: {len(entries)}\n",
        "| # | Name | Type | Source Skill | Task | Size |",
        "|---|------|------|-------------|------|------|",
    ]

    type_counts: dict[str, int] = {}
    for e in entries:
        size_kb = e["size_bytes"] / 1024
        lines.append(
            f"| {e['id']} | `{e['name']}` | {e['type']} | {e['source_skill']} "
            f"| {e['source_task']} | {size_kb:.1f} KB |"
        )
        type_counts[e["type"]] = type_counts.get(e["type"], 0) + 1

    lines.append("\n## By Type\n")
    for t, count in sorted(type_counts.items()):
        lines.append(f"- **{t}**: {count}")

    report = "\n".join(lines)

    if output:
        output.write_text(report, encoding="utf-8")
        print(f"✅ Report written to {output}")
    else:
        print(report)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Artifacts Maker — registry & manifest")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Initialize artifacts/ directory")

    p_add = sub.add_parser("add", help="Register a new artifact")
    p_add.add_argument("--file", type=Path, required=True)
    p_add.add_argument("--type", dest="artifact_type", default=None)
    p_add.add_argument("--task-id", default="unknown")
    p_add.add_argument("--skill", default="unknown")
    p_add.add_argument("--description", default="")

    p_list = sub.add_parser("list", help="List artifacts")
    p_list.add_argument("--type", dest="artifact_type", default=None)

    p_val = sub.add_parser("validate", help="Validate artifact against type schema")
    p_val.add_argument("--file", type=Path, required=True)
    p_val.add_argument("--type", dest="artifact_type", required=True)

    p_rep = sub.add_parser("report", help="Generate Markdown summary")
    p_rep.add_argument("--output", type=Path, default=None)

    args = parser.parse_args()

    if args.command == "init":
        cmd_init()
    elif args.command == "add":
        cmd_add(args.file, args.artifact_type, args.task_id, args.skill, args.description)
    elif args.command == "list":
        cmd_list(args.artifact_type)
    elif args.command == "validate":
        cmd_validate(args.file, args.artifact_type)
    elif args.command == "report":
        cmd_report(args.output)


if __name__ == "__main__":
    main()
