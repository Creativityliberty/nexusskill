---
name: skill-architect
description: Multi-agent pipeline that analyzes, refactors, reviews, audits, and documents an existing Claude Code skill. Use when the user wants to improve a skill, audit a skill for security, optimize skill structure, or get expert feedback on a SKILL.md. Inspired by the Architect Studio Blueprint Forge. Triggers on "improve this skill", "audit my skill", "refactor skill", "optimize skill", "review my skill", "/skill-architect".
---

# Skill Architect — Multi-Agent Pipeline

Transforms an existing skill through 5 specialized agent roles executed in sequence.
Each role adopts a distinct perspective to produce a production-ready skill.

## Input

Ask the user to provide:
- The skill folder path (e.g. `skills/my-skill/`) **or**
- The SKILL.md content directly

Read all files in the skill: SKILL.md, any scripts, references, assets.

## Pipeline — 5 Agent Roles

Work through each role in order. Use a todo list to track progress.
For each role: adopt the mindset, produce structured output, then continue.

---

### Role 1 — Architecture Analyst

**Mindset**: "What is this skill's structure and where are the weaknesses?"

Produce a `SkillArchitecture` report:

```
## 🏗️ Architecture Analysis

**Components found:**
- [ ] SKILL.md
- [ ] scripts/
- [ ] references/
- [ ] assets/

**Dependencies:** (e.g. SKILL.md → references/api.md)

**Concerns:**
- [concern 1]
- [concern 2]
```

Check for:
- Is description comprehensive enough to trigger correctly?
- Does SKILL.md body exceed 500 lines? (should move content to references/)
- Are references linked explicitly from SKILL.md?
- Are scripts listed and their purpose clear?
- Is there extraneous documentation (README, CHANGELOG) that should be removed?

---

### Role 2 — Code Refactorer

**Mindset**: "How can scripts be cleaner, more robust, and more reliable?"

Produce a `CodeRefactoringPlan`:

```
## 🔧 Code Refactoring Plan

**scripts/my_script.py:**
- Add error handling for [case]
- Add logging for [operation]
- Extract [logic] into helper function

**SKILL.md updates needed:**
- [update description of script usage if behavior changes]
```

For each script:
- Add proper error handling and informative error messages
- Add logging/progress output for long operations
- Remove hardcoded values → use parameters
- Ensure idempotency (safe to run multiple times)
- Check for shell injection if using subprocess

If no scripts exist: note that scripts/ is not needed, or suggest one if the skill would benefit.

---

### Role 3 — Skill Reviewer

**Mindset**: "Is this skill high quality? Will Claude use it correctly?"

Produce `ReviewFeedback`:

```
## 👁️ Review Feedback  [Priority: High / Medium / Low]

**Suggestions:**
- [ ] [suggestion 1]
- [ ] [suggestion 2]

**What works well:**
- [positive 1]
```

Review criteria:
- Does the description cover all trigger phrases?
- Is the workflow clear and actionable?
- Are degrees of freedom appropriate (free-form vs. exact scripts)?
- Are edge cases handled?
- Progressive disclosure: is content split correctly across files?
- Would another Claude instance understand and execute this correctly?

---

### Role 4 — Security Auditor

**Mindset**: "What could go wrong? What could be exploited?"

Produce `SecurityAuditReport`:

```
## 🔒 Security Audit

**Vulnerabilities found:**
- [vuln 1] — [file:line]

**Recommendations:**
- [fix 1]
- [fix 2]
```

Check for:
- Shell injection in bash commands (unquoted variables, `eval`, backticks)
- Command injection via user input passed to subprocess
- Secrets or credentials hardcoded in scripts
- `input()` calls (Python) without sanitization
- File path traversal (unsanitized paths from user input)
- Overly broad `chmod 777` or similar
- Network requests without timeout or certificate validation

If no vulnerabilities: state `✅ No vulnerabilities found.`

---

### Role 5 — Documentation Enhancer

**Mindset**: "Will a new user immediately understand how to use this?"

Produce `EnhancedDocumentation`:

```
## 📝 Documentation Improvements

**Description improvements:**
[improved frontmatter description]

**Usage examples to add:**
- "Say: [trigger phrase] → Claude will [outcome]"
- "Say: [trigger phrase] → Claude will [outcome]"

**Wrap-up section:**
[suggested wrap-up summary format for the skill]
```

Improve:
- Frontmatter `description`: make it richer with more trigger phrases
- Add a "Wrap Up" section if missing
- Add concrete examples of what the user should say
- Clarify ambiguous steps

---

## Output

After all 5 roles complete, produce the **improved skill files**:

1. Rewrite `SKILL.md` incorporating all improvements
2. Rewrite/create any scripts with security + refactoring fixes applied
3. Add/update reference files if content was moved from SKILL.md

Show a final summary:

```
## ✅ Skill Architect — Complete

| Role | Status | Key finding |
|------|--------|-------------|
| Architecture Analyst | ✅ | [finding] |
| Code Refactorer | ✅ | [finding] |
| Skill Reviewer | ✅ | [finding] |
| Security Auditor | ✅ | [finding] |
| Documentation Enhancer | ✅ | [finding] |

**Files updated:** SKILL.md [+ scripts/... + references/...]
```

Ask: "Do you want me to write these improvements directly to the skill files?"

## Reference

See [references/agent-roles.md](references/agent-roles.md) for detailed checklists per role.
See [scripts/skill_pipeline.py](scripts/skill_pipeline.py) for the data model / pipeline blueprint.
