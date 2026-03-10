# Agent-Native Profiles

Derived from analysis of 32 AI tool system prompts. Each profile describes how an agent
internally processes skills, what conventions it expects, and how to optimize SKILL.md
content for maximum effectiveness.

## Profile Schema

Each agent profile contains:
- **Skill reading**: How the agent discovers and loads skills
- **Preferred format**: What content structure works best
- **XML tags**: Agent-specific tags the skill can leverage
- **Tool names**: Internal tool names the skill should reference
- **Context strategy**: How to optimize for the agent's context window
- **Tone**: What instruction style the agent responds to best

---

## Claude Code (Anthropic)

**Skill reading**: YAML frontmatter → description triggers loading → body read on match
**Preferred format**: Markdown with YAML frontmatter. Progressive disclosure: metadata →
SKILL.md body → references/ directory for overflow.

**Key XML tags the agent recognizes**:
- `<artifact_instructions>` — for structured output templates
- `<tool_usage>` — tool calling guidance
- `<computer_use>` — file and shell operations
- `<search_instructions>` — web search guidance
- `<available_skills>` — skill discovery context

**Internal tools**: `bash`, `str_replace`, `view`, `create_file`, `present_files`,
`web_search`, `web_fetch`

**Context strategy**: Keep SKILL.md concise (<500 lines). Use references/ for large
content. The agent reads SKILL.md first, then follows pointers to references/ as needed.

**Tone**: Explain the WHY behind instructions. Use imperative form but with reasoning.
Avoid heavy-handed MUSTs — explain reasoning instead. Include examples.

**Description optimization**: The description field (≤1024 chars) is the PRIMARY trigger.
Make it "pushy" — list all scenarios. Claude tends to "undertrigger" skills.

---

## Cursor

**Skill reading**: `.cursor/skills/` directory or `.cursorrules` integration.
**Preferred format**: Dense, imperative markdown. Minimal formatting.

**Key conventions**:
- Uses `@` symbol for file/symbol references in UI
- Supports `.cursorrules` for project-level instructions
- Inline completion oriented — patterns and examples matter most

**Internal tools**: `codebase_search`, `edit_file`, `read_file`, `grep_search`,
`file_search`, `list_dir`, `run_terminal_cmd`

**Context strategy**: Cursor has aggressive context management. Put critical info FIRST.
The agent may truncate long skills. Front-load the most important patterns.

**Tone**: Terse, imperative. "Do X. Never Y. Always Z." Code examples > prose.

**Optimization tips**:
- Include file path patterns for context matching
- Add code blocks for every common operation
- List forbidden patterns explicitly
- Keep under 200 lines for best results

---

## Windsurf (Codeium)

**Skill reading**: `.windsurf/skills/` directory + `.windsurfrules` config.
**Preferred format**: Step-by-step workflows (cascade pattern).

**Key conventions**:
- Cascade mode: multi-step agentic workflows
- Flow-based execution model
- Supports browser and terminal tools

**Internal tools**: `create_file`, `edit_file`, `read_file`, `run_command`,
`search`, `browser`, `deploy`

**Context strategy**: Windsurf handles long contexts well. Can be more verbose than Cursor.
Structure with clear headings and step numbers.

**Tone**: Structured, workflow-oriented. "Step 1: ... Step 2: ..." format works well.

---

## GitHub Copilot

**Skill reading**: `.agents/skills/` (universal agent). No symlinks needed.
**Preferred format**: Standard markdown. Completion-oriented.

**Key conventions**:
- Primarily code completion, not agentic
- Learns patterns from examples more than instructions
- Context comes from open files, not skill files directly (for inline completion)
- Copilot Chat and Copilot Workspace are more skill-aware

**Internal tools**: Varies by mode (Chat vs Workspace vs inline)

**Context strategy**: Include LOTS of code examples. Pattern-based learning.
Show the input→output transformation clearly.

**Tone**: Example-heavy. Show don't tell. Include code comments as guidance.

---

## Cline

**Skill reading**: `.cline/skills/` directory + `.cline/settings.json`.
**Preferred format**: Tool-use oriented with explicit examples.

**Key XML tags the agent recognizes**:
- `<ask_followup_question>` — when to ask for clarification
- `<attempt_completion>` — completion signaling
- `<environment_details>` — context injection
- `<read_file>`, `<write_to_file>`, `<execute_command>` — tool patterns

**Internal tools**: `read_file`, `write_to_file`, `replace_in_file`,
`search_files`, `list_files`, `execute_command`, `ask_followup_question`,
`attempt_completion`, `browser_action`

**Context strategy**: Cline streams tools sequentially. Structure skills as
decision trees: "If X → use tool Y. If Z → use tool W."

**Tone**: Explicit and procedural. Include tool call examples.

---

## Roo Code

**Skill reading**: `.roo/skills/` directory.
**Preferred format**: Similar to Cline (forked from Cline architecture).

**Key conventions**: Same tool patterns as Cline but with mode system
(Code, Architect, Ask, Debug modes). Optimize for the Code mode by default.

**Internal tools**: Same as Cline.

**Tone**: Same as Cline but can include mode-switching hints.

---

## Augment

**Skill reading**: `.augment/skills/` directory.
**Preferred format**: Context-rich, multi-file aware.

**Key XML tags**:
- `<augment_code_snippet>` — code context blocks

**Internal tools**: `codebase_search`, `file_read`, `file_write`,
`file_str_replace`, `shell_exec`

**Context strategy**: Augment excels at cross-file understanding. Include
dependency graphs and file relationship descriptions.

**Tone**: Technical, detailed. Include architecture context.

---

## Continue

**Skill reading**: `.continue/skills/` + `.continue/config.json`.
**Preferred format**: Markdown with JSON config integration.

**Key conventions**: Open-source, highly configurable. Supports custom
model backends. Skills should be model-agnostic.

**Internal tools**: Varies by configuration (supports many backends).

**Tone**: Flexible, include configuration examples.

---

## Trae

**Skill reading**: `.trae/skills/` directory.
**Preferred format**: Standard markdown, well-structured.

**Internal tools**: `file_read`, `file_write`, `edit_file`, `run_command`,
`search`, `browser_navigate`, `browser_click`

**Context strategy**: Include clear section boundaries. Trae respects
heading hierarchy for navigation.

**Tone**: Clear, structured. Step-by-step for complex operations.

---

## Gemini CLI / OpenCode / Amp / Codex / Kimi Code CLI

**Skill reading**: `.agents/skills/` (all universal agents).
**Preferred format**: Clean standard markdown. No custom tags.

**Context strategy**: These agents read `.agents/skills/` directly.
Use the most universal, portable markdown possible. No agent-specific
conventions — pure content.

**Tone**: Clear, technical, well-organized. Works for any agent.

---

## Meta-Patterns Across All Agents

From analyzing 32 system prompts, these patterns are universal:

**Always effective:**
- Code examples with full context (imports, setup, usage)
- Imperative instructions ("Use X", "Run Y", "Never do Z")
- Clear heading hierarchy (H2 for sections, H3 for subsections)
- Tables for reference data (API params, config options)
- Troubleshooting sections with error→solution pairs

**Never effective:**
- Vague instructions ("consider using...", "you might want to...")
- Walls of text without structure
- Abstract descriptions without concrete examples
- Instructions that contradict the agent's built-in behavior

**Context window priorities (universal):**
1. What the tool/library IS (1 sentence)
2. How to install/import it
3. Most common operations (with code)
4. Configuration reference
5. Edge cases and gotchas
6. Full API reference (overflow to references/)
