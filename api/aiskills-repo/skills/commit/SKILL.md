---
name: commit
description: Create well-formatted git commits. Use when the user wants to commit changes, stage files, write a commit message, or run a git commit workflow. Triggers on requests like "commit my changes", "make a commit", "/commit".
---

# Commit Skill

Create clean, descriptive git commits following best practices.

## Workflow

### 1. Assess the Situation

Run in parallel:
```bash
git status          # see untracked/modified files
git diff --staged   # see already-staged changes
git diff            # see unstaged changes
git log --oneline -5  # understand commit message style used in this repo
```

### 2. Understand the Changes

Read relevant changed files if needed to understand what was modified and why.

### 3. Stage Files

Stage only relevant files — never blindly `git add .`:
```bash
git add <specific-files>
```

Warn the user and skip files that look sensitive (`.env`, `*.key`, `credentials.*`, `secrets.*`).

### 4. Write the Commit Message

Follow the repo's existing style. If no clear style, use Conventional Commits:

```
<type>(<scope>): <short summary>

<optional body explaining the why>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `style`, `perf`

Rules:
- Subject line ≤ 72 chars, imperative mood ("add" not "added")
- Body explains *why*, not *what*
- Reference issues if relevant: `Fixes #123`

### 5. Commit

```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <summary>

<body if needed>
EOF
)"
```

### 6. Confirm

Show the commit hash and summary. Ask if the user wants to push.

## Wrap Up

- ✅ Files staged
- ✅ Commit created: `<hash> <message>`
- Ask: "Do you want to push to `<current-branch>`?"
