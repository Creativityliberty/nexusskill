---
name: task-tree
description: Decompose a complex goal into a hierarchical DAG (Directed Acyclic Graph) of tasks. Each task maps to a skill, has explicit dependencies, and declares its expected output artifact. Used as Phase 1 of the workflow system. Triggers on "decompose this goal", "create a task tree", "break down this project", "plan tasks for", "/task-tree". Also auto-triggered by the workflow skill.
---

# Task Tree

Decompose a complex goal into a structured DAG of tasks.
Each leaf task maps to a skill + expected artifact. Dependency order drives execution.

## Output Format

```yaml
goal: "Build a complete MVP landing page for a fintech app"
version: "1.0"
created_at: "2026-02-21T10:00:00Z"
tasks:
  - id: t1
    name: "Generate design system"
    description: "Create color tokens, typography, and CSS vars"
    skill: ui-style-generator
    input:
      prompt: "fintech dashboard, dark minimal, trust-inspiring"
    output_artifact: styleguide.md
    artifact_type: markdown
    depends_on: []
    parallel_with: [t2]
    estimated_morsels: 2

  - id: t2
    name: "Scaffold project structure"
    description: "Create folders, package.json, tsconfig"
    skill: null
    input: {}
    output_artifact: project-scaffold.txt
    artifact_type: text
    depends_on: []
    parallel_with: [t1]
    estimated_morsels: 1

  - id: t3
    name: "Commit initial files"
    description: "Stage and commit the scaffold + styleguide"
    skill: commit
    input:
      message_hint: "feat: initial project scaffold with design system"
    output_artifact: commit-hash.txt
    artifact_type: commit
    depends_on: [t1, t2]
    estimated_morsels: 1
```

## Workflow

### 1. Understand the Goal

If the user hasn't fully specified:
- Ask: "What is the final deliverable?"
- Ask: "What skills should be used?" (or auto-select from skill registry)
- Ask: "Are there any constraints?" (tech stack, time, existing files)

### 2. Build the DAG

For each task:
- **id**: sequential `t1`, `t2`, `t3`...
- **skill**: which skill handles it (`null` if Claude does it directly)
- **depends_on**: list of task IDs that must complete first
- **parallel_with**: tasks that can run simultaneously
- **output_artifact**: the file/output this task produces
- **estimated_morsels**: rough count of atomic steps needed

Use decomposition strategies from [references/decomposition-strategies.md](references/decomposition-strategies.md).

### 3. Generate the ASCII Tree

Render a visual before writing the YAML:

```
Goal: Build MVP landing page
│
├── [t1] Generate design system (ui-style-generator) ──┐ parallel
├── [t2] Scaffold project (direct)               ──────┘
│
└── [t3] Commit initial files (commit)
         depends on: t1, t2
```

### 4. Write the Task Tree File

Save as `task-tree.yaml` (or `.workflow/task-tree.yaml` if inside a workflow run).

Use `scripts/task_tree.py` to generate + validate:

```bash
python skills/task-tree/scripts/task_tree.py generate \
  --goal "Build MVP landing page" \
  --output task-tree.yaml
```

Or validate an existing tree:

```bash
python skills/task-tree/scripts/task_tree.py validate --file task-tree.yaml
python skills/task-tree/scripts/task_tree.py render --file task-tree.yaml
```

### 5. Check for Cycles

The task tree must be a valid DAG (no circular dependencies).
`task_tree.py validate` checks this automatically.

## Wrap Up

- ✅ Task tree generated: `task-tree.yaml` (`N` tasks)
- Show ASCII tree
- Show: total estimated morsels, parallelizable tasks, critical path
- Ask: "Ready to execute? Run with the `workflow` or `morsel-tasks` skill."
