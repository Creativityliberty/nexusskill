# Agent Roles — Detailed Checklists

## Table of Contents
1. [Architecture Analyst](#1-architecture-analyst)
2. [Code Refactorer](#2-code-refactorer)
3. [Skill Reviewer](#3-skill-reviewer)
4. [Security Auditor](#4-security-auditor)
5. [Documentation Enhancer](#5-documentation-enhancer)

---

## 1. Architecture Analyst

**Goal**: Map the skill's components and identify structural problems.

### Checklist

**Structure**
- [ ] Does the skill have a `SKILL.md`?
- [ ] Is the folder name consistent with `name:` in frontmatter?
- [ ] Are there extraneous files (README, CHANGELOG, docs) that should not exist?
- [ ] Is the directory structure flat (references one level deep from SKILL.md)?

**SKILL.md size**
- [ ] Is the body under 500 lines? If not → move content to `references/`
- [ ] Is content split logically? (variants in separate reference files)

**Dependencies**
- [ ] Are all `references/*.md` files mentioned explicitly in SKILL.md?
- [ ] Are all `scripts/` files mentioned explicitly in SKILL.md?
- [ ] Are `assets/` files listed with purpose?

**Output format**:
```json
{
  "components": ["SKILL.md", "scripts/", "references/"],
  "dependencies": { "SKILL.md": ["references/api.md"] },
  "concerns": ["Body exceeds 500 lines", "Reference file not linked"]
}
```

---

## 2. Code Refactorer

**Goal**: Make scripts cleaner, more reliable, and secure.

### Python Script Checklist
- [ ] Uses `argparse` or clear CLI interface (not hardcoded values)
- [ ] All file operations wrapped in `try/except` with informative errors
- [ ] Uses `pathlib.Path` not raw strings for file paths
- [ ] Has `if __name__ == "__main__":` guard
- [ ] No `input()` calls without sanitization
- [ ] No `eval()` or `exec()` on user input
- [ ] Logging with `logging` module (not bare `print`)
- [ ] Functions have docstrings
- [ ] No hardcoded secrets/tokens/paths

### Bash Script Checklist
- [ ] Starts with `set -euo pipefail`
- [ ] All variables quoted: `"$VAR"` not `$VAR`
- [ ] No `eval` on external input
- [ ] Uses `mktemp` for temp files (not hardcoded `/tmp/file`)
- [ ] Cleanup with `trap ... EXIT`
- [ ] Idempotent (safe to run multiple times)

### TypeScript/JS Script Checklist
- [ ] Proper TypeScript types (no `any`)
- [ ] `async/await` with `try/catch`
- [ ] Input validation before use
- [ ] No `eval()` or `new Function()`
- [ ] Dependencies listed (what needs to be installed)

---

## 3. Skill Reviewer

**Goal**: Ensure the skill works correctly from Claude's perspective.

### Description Quality
- [ ] Mentions what the skill DOES
- [ ] Mentions all trigger phrases ("use when...", "triggers on...")
- [ ] Covers edge cases (e.g. "also use when the user says X")
- [ ] Between 50-150 words (comprehensive but not bloated)

### Body Quality
- [ ] Uses imperative form ("Run", "Read", "Generate" not "You should run")
- [ ] Has clear numbered steps
- [ ] Has a "Wrap Up" section with ✅ summary format
- [ ] References are linked with `[file.md](path/file.md)` and say WHEN to read them
- [ ] Degrees of freedom match task complexity (free text vs. exact commands)

### Workflow Completeness
- [ ] Handles the happy path
- [ ] Mentions what to do when things fail
- [ ] User is asked for missing info before proceeding
- [ ] Output is actionable (saves files, shows result, asks for confirmation)

---

## 4. Security Auditor

**Goal**: Identify vulnerabilities before the skill goes into production.

### Critical (fix immediately)
- Shell injection via unquoted variables: `rm $DIR` → should be `rm "$DIR"`
- Command injection: `subprocess.run(user_input, shell=True)` → use list form
- Secrets hardcoded in scripts or SKILL.md
- `eval()` on any external input
- Path traversal: `open(user_path)` without validation

### High
- Missing input validation before file operations
- `chmod 777` or overly permissive file permissions
- Network requests without TLS verification (`verify=False`)
- No timeout on network calls

### Medium
- `input()` in Python without sanitization note
- Missing `set -euo pipefail` in bash scripts
- Temp files in predictable locations
- Missing error handling that could expose stack traces to users

### Low / Informational
- No logging of operations
- Missing rate limiting on API calls
- Deprecated or vulnerable dependencies

---

## 5. Documentation Enhancer

**Goal**: Make the skill immediately usable by anyone.

### Frontmatter Description Template
```yaml
description: >
  [What the skill does in one sentence].
  Use when [specific trigger condition 1],
  [trigger condition 2], or [trigger condition 3].
  Triggers on "[phrase 1]", "[phrase 2]", "/skill-name".
```

### Body Improvements
- **Examples**: Add 2-3 concrete "Say X → Claude does Y" examples
- **Wrap Up section**: Always end with a summary block:
  ```
  ## Wrap Up
  - ✅ [outcome 1]
  - ✅ [outcome 2]
  - Ask: "[follow-up question]"
  ```
- **Error guidance**: "If X fails, do Y"
- **Progressive disclosure**: Move verbose detail to references/, keep SKILL.md scannable

### Anti-patterns to fix
- Vague descriptions: "helps with coding" → "generates TypeScript interfaces from JSON schemas"
- Missing triggers: description has no "use when" or trigger phrases
- Wall of text: no headers, no steps, no structure
- Missing wrap-up: user doesn't know when the skill is done
