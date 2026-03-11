# Decomposition Strategies

## Table of Contents
1. [Core Principle](#core-principle)
2. [By Goal Type](#by-goal-type)
3. [DAG Patterns](#dag-patterns)
4. [Task Sizing Rules](#task-sizing-rules)
5. [Skill Mapping Guide](#skill-mapping-guide)

---

## Core Principle

**Separate thinking from execution.**

A task tree should be built so that:
- Each leaf task is **independently executable** by one skill (or Claude directly)
- Each task produces **exactly one artifact**
- Dependencies are **explicit and minimal** (prefer parallel over sequential)
- The tree can be **re-planned** if a task fails (Loop-Back Planning)

---

## By Goal Type

### "Build a UI / Frontend"

```
t1: Generate design system        → skill: ui-style-generator     (parallel)
t2: Scaffold project structure    → skill: null / num-agents       (parallel)
t3: Implement components          → skill: null                    (depends: t1, t2)
t4: Commit & push                 → skill: commit                  (depends: t3)
t5: Open PR                       → skill: review-pr               (depends: t4)
```

### "Create an AI Agent"

```
t1: Define agent spec (YAML)       → skill: num-agents             (parallel)
t2: Design system tokens           → skill: ui-style-generator     (parallel, optional)
t3: Scaffold agent code            → skill: num-agents             (depends: t1)
t4: Implement node logic           → skill: null                   (depends: t3)
t5: Write tests                    → skill: null                   (depends: t4)
t6: Commit                         → skill: commit                 (depends: t4, t5)
```

### "Improve an existing Skill"

```
t1: Run skill-architect pipeline   → skill: skill-architect        (no deps)
t2: Apply refactoring suggestions  → skill: null                   (depends: t1)
t3: Update documentation           → skill: skill-creator          (depends: t2)
t4: Commit changes                 → skill: commit                 (depends: t2, t3)
```

### "SaaS MVP End-to-End"

```
t1: UI Design system               → ui-style-generator           (parallel batch)
t2: Agent architecture             → num-agents                    (parallel batch)
t3: Backend scaffolding            → null                          (depends: t2)
t4: Frontend scaffolding           → null                          (depends: t1)
t5: DB schema                      → null                          (depends: t2)
t6: API integration                → null                          (depends: t3, t5)
t7: Connect frontend ↔ backend     → null                          (depends: t4, t6)
t8: Code review                    → review-pr                     (depends: t7)
t9: Commit & tag                   → commit                        (depends: t8)
```

---

## DAG Patterns

### Sequential (simple pipeline)
```yaml
t1 → t2 → t3 → t4
```
Use when: each step strictly depends on the previous.

### Parallel Fan-Out + Merge
```yaml
        ┌── t2 ──┐
t1 ─────┤        ├── t4
        └── t3 ──┘
```
```yaml
- id: t2
  depends_on: [t1]
  parallel_with: [t3]
- id: t3
  depends_on: [t1]
  parallel_with: [t2]
- id: t4
  depends_on: [t2, t3]
```

### Diamond (two paths, one merge)
```yaml
        ┌── t2 (design) ──┐
t1 ─────┤                  ├── t4 (integrate)
        └── t3 (code)  ───┘
```

### Loop-Back (re-planning trigger)
```yaml
t1 → t2 → [FAIL] → re-plan → t1' → t2' → t3
```
Handled by `workflow` skill's Dynamic Router — not in the tree itself.

---

## Task Sizing Rules

| Morsels | Task size | Rule |
|---------|-----------|------|
| 1 | Nano | Single operation (one CLI call, one file write) |
| 2-3 | Small | One skill invocation with validation |
| 4-6 | Medium | Multi-step skill workflow |
| 7-10 | Large | Consider splitting into sub-tasks |
| >10 | Too large | **Split the task** |

**Golden rule**: if a task takes more than one skill to complete, split it.

---

## Skill Mapping Guide

| I need to... | Use skill |
|-------------|-----------|
| Create a visual identity / UI tokens | `ui-style-generator` |
| Make a git commit | `commit` |
| Review code changes | `review-pr` |
| Build an AI agent | `num-agents` |
| Create/improve a skill | `skill-creator` |
| Audit a skill | `skill-architect` |
| Build LLM workflows | `pocketflow` |
| Set up web session deps | `session-start-hook` |
| Custom keyboard shortcuts | `keybindings-help` |
| Execute multiple skills in order | `workflow` |
| Collect & index outputs | `artifacts-maker` |
| Break down complex goals | `task-tree` (recursive) |
| Execute atomic steps | `morsel-tasks` |
| Write code directly | `null` (Claude handles it) |
