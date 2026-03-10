# llms.txt Specification Reference

Quick reference for the llms.txt standard and related formats.

## llms.txt Format (from llmstxt.org)

The file is placed at the root path `/llms.txt` of a website.

### Required Structure

```markdown
# Project Name

> Short summary of the project with key info for understanding the rest.

Optional paragraphs with additional context.

## Section Name

- [Link Title](URL): Description of the linked resource
- [Another Link](URL): Description

## Optional

- [Resource](URL): Lower-priority resource description
```

### Rules

1. **H1** (required): Project or site name — exactly one
2. **Blockquote**: Short summary — strongly recommended
3. **Body paragraphs**: Additional context — optional
4. **H2 sections**: Group related links — use descriptive names
5. **Link lists**: `- [Title](URL): Description` format
6. **"Optional" section**: Lower-priority resources go under `## Optional`

### Best Practices

- Keep llms.txt under 10KB for the index version
- Use clear, descriptive link titles
- Write descriptions that help LLMs decide whether to fetch the full resource
- Group logically: Docs, API, Guides, Examples, etc.
- Link to .md files when possible (lower token cost than HTML)

## llms-full.txt Format

Complete documentation inline. Same header format, but sections contain full content
instead of links. Aim for <500KB.

## SKILL.md Format (for AI Agent Skills)

```markdown
---
name: skill-slug
description: >
  When to trigger this skill and what it does.
  Be comprehensive and slightly "pushy" in listing trigger conditions.
---

# Skill Title

{Documentation content optimized for AI consumption}
```

### Frontmatter Fields

- `name` (required): Kebab-case identifier
- `description` (required): Trigger conditions and purpose — this is the PRIMARY
  mechanism for skill activation. Include all relevant keywords and contexts.

### Content Guidelines

- Keep under 500 lines
- Use references/ directory for overflow content
- Include code examples
- Start with most commonly needed info
- Organize by topic, not by source page

## File Size Guidelines

| File | Target | Max |
|------|--------|-----|
| llms.txt | <10KB | 50KB |
| llms-full.txt | <100KB | 500KB |
| SKILL.md | <200 lines | 500 lines |
| references/*.md | <300 lines each | No hard limit |

## Registry Slug Convention

Slugs use kebab-case derived from the package/project name:
- `react` → `react`
- `Next.js` → `next-js`
- `Tailwind CSS` → `tailwindcss`
- `Vercel AI SDK` → `vercel-ai-sdk`
