---
name: review-pr
description: Review a GitHub Pull Request — analyze code changes, spot bugs, check style, assess tests, and write a structured review comment. Use when the user says "review this PR", "review PR #123", "/review-pr", or asks for a code review on a pull request.
---

# Review PR Skill

Perform thorough, actionable pull request reviews.

## Workflow

### 1. Get the PR

If a PR number or URL is provided:
```bash
gh pr view <number> --json title,body,author,baseRefName,headRefName,files,additions,deletions
gh pr diff <number>
```

If no PR is specified, use the current branch:
```bash
gh pr view --json title,body,files
gh pr diff
```

### 2. Read the Context

- Read the PR title and description to understand intent
- List changed files and their diff sizes
- For large diffs (>500 lines), focus on the most critical files first

### 3. Analyze the Changes

For each changed file, evaluate:

**Correctness**
- Logic errors, off-by-one, null/undefined handling
- Edge cases not covered
- Race conditions or concurrency issues

**Security**
- SQL injection, XSS, command injection
- Secrets or credentials in code
- Auth/permission issues
- Input validation at boundaries

**Design**
- Does it follow existing patterns in the codebase?
- Is complexity justified?
- Are abstractions appropriate (not too early, not too late)?

**Tests**
- Are new behaviors tested?
- Are edge cases covered?
- Do existing tests still make sense?

**Readability**
- Variable/function names clear?
- Complex logic commented?

### 4. Write the Review

Structure the review as:

```markdown
## Summary
<1-3 sentences: what the PR does and overall assessment>

## 🔴 Must Fix
- `file.py:42` — <issue> because <reason>

## 🟡 Suggestions
- `file.py:87` — Consider <improvement> for <reason>

## 🟢 Looks Good
- <what was done well>

## Questions
- <anything unclear that needs author clarification>
```

Severity guide:
- 🔴 **Must Fix**: bugs, security issues, broken tests
- 🟡 **Suggestion**: style, performance, better patterns
- 🟢 **Looks Good**: acknowledge quality work

### 5. Post or Display

If the user wants to post the review:
```bash
gh pr review <number> --comment --body "<review>"
# or for approval:
gh pr review <number> --approve --body "<review>"
# or to request changes:
gh pr review <number> --request-changes --body "<review>"
```

Otherwise, display the review to the user.

## Wrap Up

- Summary of findings
- Count of 🔴 must-fix / 🟡 suggestions / 🟢 positives
- Recommended action: approve / request changes / comment
