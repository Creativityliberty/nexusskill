---
name: skill-creator
description: Guide for creating effective Claude Code skills. Use when the user wants to create a new skill, update an existing skill, or learn how to structure a skill. Triggers on "create a skill", "make a skill", "add a skill", "/skill-creator".
---

# Skill Creator

Skills are self-contained packages that extend Claude's capabilities with specialized workflows, domain knowledge, and reusable resources.

## Anatomy of a Skill

```
skill-name/
├── SKILL.md              ← required: frontmatter + instructions
├── scripts/              ← optional: executable code (Python/Bash)
├── references/           ← optional: docs loaded into context as needed
└── assets/               ← optional: templates, images, fonts used in output
```

### SKILL.md Frontmatter

Only `name` and `description` are required. The description is the **primary trigger** — write it to cover all "when to use" cases, because the body only loads after the skill triggers.

```yaml
---
name: my-skill
description: What this skill does and when to use it. Include all trigger phrases and use cases here. Example: "Use when the user wants to X, Y, or Z. Triggered by 'do X', '/my-skill', or 'help me with Y'."
---
```

### Body: Degrees of Freedom

Match specificity to the task:

| Task type | Use |
|-----------|-----|
| Many valid approaches | Free-form text instructions |
| Preferred pattern with some variation | Pseudocode or parameterized scripts |
| Fragile, must be exact | Specific scripts with few params |

## Core Principles

**Concise is key** — Context window is shared. Only include what Claude doesn't already know.

**Progressive disclosure** — Keep SKILL.md under 500 lines. Move detailed content to `references/` files and link them explicitly from SKILL.md.

**No extra docs** — No README.md, CHANGELOG.md, INSTALLATION.md in the skill. Only files the AI agent needs.

## Creation Process

### 1. Understand with Examples

Ask the user:
- What tasks should this skill handle?
- Give 2-3 concrete examples of how it would be used.
- What should trigger it?

### 2. Plan Resources

For each example, think:
- Is there code that gets rewritten repeatedly? → `scripts/`
- Is there domain knowledge Claude needs? → `references/`
- Are there templates/files used in output? → `assets/`

### 3. Create the Skill Directory

```bash
mkdir -p skills/my-skill/scripts skills/my-skill/references skills/my-skill/assets
```

Delete unused subdirectories.

### 4. Write SKILL.md

- **Frontmatter**: `name` + comprehensive `description`
- **Body**: Workflow steps, key commands, when to use references
- If supporting multiple variants (AWS/GCP/Azure, React/Vue/etc.), keep SKILL.md lean and use `references/<variant>.md`

### 5. Add Bundled Resources

**Scripts** — Write, then test by actually running them:
```bash
python skills/my-skill/scripts/my_script.py
```

**References** — Documentation, schemas, API specs. For files >100 lines, add a table of contents at the top.

**Assets** — Templates or boilerplate to copy/modify (not loaded into context, used in output).

### 6. Validate Structure

```
✅ SKILL.md has name + description in frontmatter
✅ Description covers all trigger cases
✅ Body is under 500 lines
✅ References linked explicitly from SKILL.md
✅ Scripts tested and working
✅ No extraneous documentation files
```

### 7. Add to This Repo

Place the skill folder in `skills/` and update `README.md` table.

## Reference File Patterns

**Pattern 1 — High-level + references:**
```markdown
## Advanced features
- Form filling: See [references/forms.md](references/forms.md)
- API reference: See [references/api.md](references/api.md)
```

**Pattern 2 — Multi-variant:**
```
cloud-deploy/
├── SKILL.md (selection logic)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

**Pattern 3 — Conditional:**
```markdown
For basic edits, modify directly.
**For tracked changes**: See [references/redlining.md](references/redlining.md)
```

Keep references one level deep — all link directly from SKILL.md.
