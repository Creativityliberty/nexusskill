---
name: artifacts-maker
description: Collect, name, organize and track all output artifacts produced during a workflow or task execution. Creates a structured artifacts/ directory with a manifest.json index. Use when a workflow produces files, code, reports, configs, or any output that needs to be tracked. Integrates with morsel-tasks and workflow skills. Triggers on "save artifacts", "collect outputs", "create artifact manifest", "track outputs", "/artifacts-maker".
---

# Artifacts Maker

Every completed task produces an artifact. This skill collects, names, organizes,
and indexes them in a structured `artifacts/` directory with a `manifest.json`.

## Output Structure

```
artifacts/
├── manifest.json              ← master index of all artifacts
├── 001_styleguide.md          ← zero-padded execution order prefix
├── 002_design-tokens.json
├── 003_commit-hash.txt
└── 004_pr-review.md
```

## Workflow

### 1. Initialize Artifacts Directory

```bash
python skills/artifacts-maker/scripts/artifact_registry.py init
```

Creates `artifacts/` + empty `manifest.json` if they don't exist.

### 2. Register an Artifact

After each task/morsel completes, register its output:

```bash
python skills/artifacts-maker/scripts/artifact_registry.py add \
  --file path/to/output.md \
  --type markdown \
  --task-id t1 \
  --skill ui-style-generator \
  --description "UI styleguide for fintech dashboard"
```

Or from Claude directly: call `artifact_registry.py add` with the completed file.

### 3. List All Artifacts

```bash
python skills/artifacts-maker/scripts/artifact_registry.py list
python skills/artifacts-maker/scripts/artifact_registry.py list --type code
```

### 4. Generate Summary Report

```bash
python skills/artifacts-maker/scripts/artifact_registry.py report
```

Outputs a Markdown summary of all artifacts for the user.

### 5. Schema Validation (Schema-First)

Each artifact type has an expected schema. Before registering, validate:

```bash
python skills/artifacts-maker/scripts/artifact_registry.py validate \
  --file output.json --type design-system
```

See [references/artifact-types.md](references/artifact-types.md) for all types + schemas.

## Artifact Types Quick Reference

| Type | Extension | Validated |
|------|-----------|-----------|
| `markdown` | `.md` | size > 0 |
| `code` | `.py .ts .js .sh` | syntax check |
| `design-system` | `.json` | Pydantic schema |
| `config` | `.yaml .json .toml` | parse check |
| `report` | `.md` | has headers |
| `commit` | `.txt` | contains hash |
| `diff` | `.patch .diff` | valid diff |
| `image` | `.png .jpg .svg` | size > 0 |

See [references/artifact-types.md](references/artifact-types.md) for full schemas.

## Wrap Up

- ✅ Artifacts saved to `artifacts/`
- ✅ manifest.json updated (`N` artifacts)
- Show table: id | name | type | source skill | size
- Ask: "Do you want a summary report? Run: `artifact_registry.py report`"
