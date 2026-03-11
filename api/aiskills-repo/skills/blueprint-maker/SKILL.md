---
name: blueprint-maker
description: Universal domain-agnostic blueprint generator. Creates structured project blueprints for ANY field — business, product, research, education, engineering, or custom. Use when user says "create a blueprint", "plan a project", "design a system", "build a strategy", "blueprint for", "/blueprint", "architect a plan". Works for tech AND non-tech domains.
---

# Blueprint Maker — Universal Project Architect

Generates comprehensive, structured blueprints for **any domain**. Not just code — business plans, research protocols, educational curricula, product specs, and more.

## When to use

- User wants to **plan** something before building it
- User needs a **structured document** for a project in any field
- User says "blueprint", "plan", "strategy", "design", "architecture"

## Step 1: Detect Domain

Ask the user what they want to build, then auto-detect the domain:

| Domain | Trigger Keywords | Template |
|--------|-----------------|----------|
| **Business** | startup, business, revenue, market, SaaS | `business.yaml` |
| **Product** | app, feature, UX, MVP, requirements | `product.yaml` |
| **Research** | study, hypothesis, experiment, data | `research.yaml` |
| **Education** | course, curriculum, learning, teach | `education.yaml` |
| **Engineering** | system, API, architecture, infra | `engineering.yaml` |
| **Custom** | anything else | `custom.yaml` |

If ambiguous, ask: "This sounds like a **[domain]** project. Is that right, or would you prefer a different blueprint style?"

## Step 2: Load Template

Read the matching template from `templates/<domain>.yaml`. Each template defines:

- **Sections**: ordered list of blueprint blocks
- **Required fields**: what must be filled
- **Optional fields**: nice-to-have sections
- **Prompts**: LLM prompts to generate each section

## Step 3: Interview (Quick)

For each required section, ask the user targeted questions. Keep it **fast** — max 3 questions:

1. **Goal**: "What's the desired outcome in one sentence?"
2. **Constraints**: "Any budget, timeline, or resource limits?"
3. **Audience**: "Who is this for?"

## Step 4: Generate Blueprint

Use the template + user answers to generate a complete markdown blueprint.

Run the engine:

```python
python scripts/blueprint_engine.py --domain <domain> --goal "<user goal>" --output blueprint.md
```

Or generate inline using the template structure.

### Blueprint Structure (all domains share this skeleton)

```markdown
# Blueprint: [Project Name]

## 📋 Executive Summary
[1-paragraph overview]

## 🎯 Objectives
- Primary: [main goal]
- Secondary: [supporting goals]

## 📊 Analysis
[Domain-specific analysis section]

## 🏗️ Architecture / Structure
[The core blueprint — phases, components, or modules]

## 📅 Timeline & Milestones
[Phased timeline with deliverables]

## 💰 Resources & Budget
[People, tools, money needed]

## ⚠️ Risks & Mitigations
[What could go wrong + how to handle it]

## 📈 Success Metrics
[How to measure success — KPIs, OKRs, etc.]

## 📎 Appendix
[References, links, raw data]
```

## Step 5: Export

Offer the user multiple formats:

- **Markdown** (default) — ready to paste anywhere
- **YAML** — machine-readable, can feed into `dag-taskview`
- **Mermaid** — visual diagram of the architecture/timeline

## Step 6: Chain to DAG

After blueprint generation, ask:
> "Want me to convert this blueprint into a **visual task DAG** with dependencies and progress tracking? (uses `dag-taskview` skill)"

## Integration

| Skill | Chain |
|---|---|
| `dag-taskview` | Blueprint phases → task DAG with dependencies |
| `orchestra-forge` | Blueprint → AI agent that executes each phase |
| `flow-orchestrator` | Run the agent with pause/resume/tracing |
| `skill-architect` | Audit the generated blueprint for quality |

## Examples

- "Create a blueprint for a fitness app" → Product template
- "Blueprint for opening a bakery in Paris" → Business template
- "Plan a machine learning research project on NLP" → Research template
- "Design a 12-week coding bootcamp curriculum" → Education template
- "Architect a microservices e-commerce backend" → Engineering template
