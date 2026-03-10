---
name: ide-setup
description: Automatically configures the project for AI-powered IDEs (Cursor, Windsurf, Trae, Cline, Roo Code). Use when the user wants to "optimize" or "setup" the project for their specific editor.
---

# IDE Setup Skill

This skill helps configure project-specific rules and instructions for various AI-enhanced IDEs, ensuring that their internal agents (like Cascade, Cursor AI, or Cline) understand the project architecture and the available `aiskills` catalog.

## Supported IDEs

- **Cursor**: Generates `.cursor/rules/aiskills.md` or `.cursorrules`.
- **Windsurf**: Generates `.windsurf/rules/aiskills.md` or `.windsurfrules`.
- **Trae**: Generates `.trae/rules/project_rules.md`.
- **Cline / Roo Code**: Generates `.clinerules`.
- **Antigravity / Claude Code**: Generates `.agent/rules/aiskills.md`.

## When to use this skill

1. When a user asks to "setup the project rules" or "configure the IDE".
2. When starting a new project that will be opened in one of the supported IDEs.
3. When you want to bridge Antigravity skills with another IDE's agent.

## How to use it

1. **Detection**: First, check for folder markers like `.cursor/`, `.trae/`, or `.windsurf/`.
2. **Setup**: Run the `scripts/setup.py` script provided in this skill.

   ```bash
   python scripts/setup.py --ide [ide-name]
   ```

3. **Verification**: Confirm to the user that the rule files have been generated and that the IDE agent should now be aware of the `aiskills` catalog.

## Patterns and Guidelines

- **Progression**: Prefer the directory-based rules (e.g., `.cursor/rules/`) over single-file legacy rules.
- **Context**: Always include a link/reference to the `D:/projet Dacko/nanoclaw/aiskills` directory so other agents can find our specialized tools.
- **Structure**: Group rules by category (Architect, Scaffold, Forge) to keep them organized.
