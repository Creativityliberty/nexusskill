# Artifact Types — Schemas & Conventions

## Table of Contents
1. [Naming Convention](#naming-convention)
2. [Type Definitions](#type-definitions)
3. [Validation Rules](#validation-rules)
4. [I/O Contracts (Schema-First)](#io-contracts)

---

## Naming Convention

All artifacts are stored as: `{seq:03d}_{original_filename}`

```
001_styleguide.md        ← first artifact produced
002_design-tokens.json
003_agent.py
004_commit-hash.txt
```

The `seq` prefix preserves execution order and prevents name collisions.

---

## Type Definitions

### `markdown`
- Extensions: `.md`
- Produced by: `ui-style-generator`, `review-pr`, `skill-architect`, `skill-creator`
- Must have: at least one `#` heading
- Validation: non-empty, has headings

### `code`
- Extensions: `.py`, `.ts`, `.js`, `.tsx`, `.sh`, `.go`, `.rs`
- Produced by: any skill that generates source code
- Validation: non-empty, syntax check if language tooling available

### `design-system`
- Extension: `.json`
- Produced by: `ui-style-generator`
- **Required fields**: `projectName`, `colors.light`, `colors.dark`, `typography`, `spacing`
- Validation: Pydantic schema (see I/O Contracts below)

### `config`
- Extensions: `.yaml`, `.yml`, `.json`, `.toml`
- Produced by: `num-agents` (agent.yaml), `workflow` (workflow.yaml)
- Validation: parseable by respective parser

### `report`
- Extension: `.md`
- Produced by: `skill-architect`, `review-pr`
- Must have: summary section + at least one list
- Validation: has `##` headings + list items

### `commit`
- Extension: `.txt`
- Produced by: `commit` skill
- Content: git commit hash + message
- Validation: first line matches `[0-9a-f]{7,40}`

### `diff`
- Extensions: `.patch`, `.diff`
- Produced by: code modification tasks
- Validation: starts with `---` or contains `@@`

### `image`
- Extensions: `.png`, `.jpg`, `.svg`, `.webp`
- Produced by: `ui-style-generator` (preview), image generation skills
- Validation: file size > 0, valid magic bytes

### `text`
- Extension: `.txt`
- Generic text output
- Validation: non-empty

---

## Validation Rules

```python
# Validation matrix
VALIDATIONS = {
    "markdown":      ["non_empty", "has_headings"],
    "code":          ["non_empty", "syntax_check"],
    "design-system": ["non_empty", "valid_json", "schema_design_system"],
    "config":        ["non_empty", "parseable"],
    "report":        ["non_empty", "has_headings", "has_lists"],
    "commit":        ["non_empty", "has_git_hash"],
    "diff":          ["non_empty", "valid_diff_format"],
    "image":         ["non_empty", "valid_binary"],
    "text":          ["non_empty"],
}
```

---

## I/O Contracts

Schema-First: each skill declares its output contract.
`morsel_runner.py` validates the output before marking the morsel as `done`.

### DesignSystem (from `ui-style-generator`)

```json
{
  "projectName": "string (required)",
  "description": "string (required)",
  "colors": {
    "light": { "primary": "#hex", "background": "#hex", "..." },
    "dark":  { "primary": "#hex", "background": "#hex", "..." }
  },
  "typography": { "fontFamily": "string", "scale": { "h1": "px", "..." } },
  "spacing": { "base": "number", "scale": { "xs": "px", "..." } },
  "gradients": { "primary": "css-gradient", "secondary": "css-gradient" },
  "shadows": { "sm": "css-shadow", "md": "...", "lg": "..." },
  "borderRadius": { "small": "px", "medium": "px", "large": "px", "full": "px" },
  "animation": { "easing": "css-easing", "duration": { "fast": "ms", "..." } },
  "layout": { "containerWidth": "px", "gridColumns": "number", "gridGap": "px" },
  "effects": { "glass": "backdrop-filter", "borderWidth": "px" },
  "iconStyle": "string"
}
```

### TaskTree (from `task-tree`)

```json
{
  "goal": "string",
  "version": "string",
  "created_at": "ISO8601",
  "tasks": [
    {
      "id": "t1",
      "name": "string",
      "description": "string",
      "skill": "skill-name | null",
      "input": {},
      "output_artifact": "filename.ext",
      "artifact_type": "artifact-type",
      "depends_on": [],
      "parallel_with": [],
      "estimated_morsels": 3
    }
  ]
}
```

### WorkflowState (from `workflow`)

```json
{
  "workflow_id": "uuid",
  "name": "string",
  "status": "pending | running | paused | done | failed",
  "current_step": "step_id",
  "steps": [
    {
      "id": "step1",
      "skill": "skill-name",
      "status": "pending | running | done | failed | skipped",
      "input": {},
      "output_artifact": "path",
      "started_at": "ISO8601",
      "completed_at": "ISO8601"
    }
  ],
  "artifacts": ["001_file.md", "002_file.json"],
  "replan_count": 0
}
```

### MorselCheckpoint (from `morsel-tasks`)

```json
{
  "workflow_id": "string",
  "task_id": "string",
  "morsels": [
    {
      "id": "m1",
      "action": "string",
      "status": "pending | running | done | failed | skipped",
      "attempt": 1,
      "output_artifact": "path | null",
      "error": "string | null",
      "completed_at": "ISO8601 | null"
    }
  ],
  "last_updated": "ISO8601"
}
```
