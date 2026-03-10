---
name: nexus
description: >
  Unified mission engine + AI-agent skill system. Intercepts any project request
  (SaaS, app, API, CLI, agent) and decomposes into Goal → Mission → Task → Flow
  with quality gates and deliverable artifacts. Also installs and generates
  llms.txt / SKILL.md for 39+ AI agents with agent-native optimization from
  32 system prompt profiles. Trigger on: project ideas, "je veux faire", "build me",
  "create a", SaaS, MVP, app, platform, skill setup, llms.txt, SKILL.md, agent docs,
  or any complex task needing structured decomposition before execution.
---

# NEXUS — Mission Engine + Agent Skill System

One system. Two modes. Every project, every agent.

```
 USER: "Je veux faire un SaaS de X"
                    ↓
 ╔═══════════════════════════════════════════╗
 ║              N E X U S                    ║
 ║                                           ║
 ║  MODE A: MISSION          MODE B: SKILLS  ║
 ║  ┌──────────────┐    ┌─────────────────┐  ║
 ║  │ INTERCEPT    │    │ DETECT stack    │  ║
 ║  │ DECOMPOSE    │    │ FETCH docs      │  ║
 ║  │ PLAN flows   │    │ GENERATE skills │  ║
 ║  │ EXECUTE+gate │    │ OPTIMIZE /agent │  ║
 ║  │ DELIVER arts │    │ INSTALL 39 dirs │  ║
 ║  └──────┬───────┘    └────────┬────────┘  ║
 ║         └─────────┬───────────┘           ║
 ║                   ▼                       ║
 ║         ARTIFACTS + SKILLS                ║
 ║    docs, code, specs, agent skills        ║
 ╚═══════════════════════════════════════════╝
```

---

## Mode Selection

NEXUS auto-detects which mode to run:

| User Says | Mode | What Happens |
|-----------|------|-------------|
| "Build me a SaaS..." | **MISSION** | Full decomposition → execution → artifacts |
| "Install skills for my project" | **SKILLS** | Detect deps → fetch → install for agents |
| "Generate llms.txt for my API" | **SKILLS** | Analyze docs → generate llms.txt + SKILL.md |
| "Create a platform with agent tools" | **BOTH** | Mission plan + agent skills installed |

When in doubt, default to **MISSION** mode — it's more comprehensive and will
invoke SKILLS mode as a task within the mission when needed.

---

## MODE A: MISSION ENGINE

### A1. INTERCEPT — Capture Intent

Extract from user's message:

| Field | Extract | Default if Missing |
|-------|---------|-------------------|
| Vision | What they want to build | — (must be stated) |
| Domain | Business/tech area | "Web application" |
| Users | Target audience | "General users" |
| Core Value | Key differentiator | First feature mentioned |
| Constraints | Stack, timeline, team | Next.js + Supabase, 6 weeks, solo dev |

Ask **max 3 questions** if critical info is missing. Otherwise, proceed with defaults.

### A2. DECOMPOSE — Build Mission Hierarchy

```
GOAL (1)
  └─ MISSION (1-3 phases)
       └─ TASK (3-8 per mission)
            └─ SUB-TASK (2-5 per task)
                 └─ FLOW (steps + gate)
```

**Goal definition:**
```yaml
goal:
  id: G-001
  title: "{Measurable goal}"
  success_criteria: ["{Metric 1}", "{Metric 2}", "{Metric 3}"]
  constraints:
    timeline: "{N weeks}"
    stack: "{Technologies}"
    team: "{Team size}"
```

**Mission breakdown** — each mission is a phase with a gate and artifacts:
```yaml
missions:
  - id: M-001
    title: "Foundation & Architecture"
    gate: "Architecture validated, scaffold running"
    artifacts: [PRD, Architecture doc, Data model, Scaffold]
  - id: M-002
    title: "Core MVP"
    gate: "Core features working end-to-end"
    artifacts: [Auth, CRUD, UI, Database]
  - id: M-003
    title: "Polish & Launch"
    gate: "Deployed, tested, documented"
    artifacts: [Tests, Landing page, Deployment, Docs]
```

**Task decomposition** — each task has sub-tasks and an artifact:
```yaml
tasks:
  - id: T-001
    mission: M-001
    title: "Define product requirements"
    artifact: "docs/prd.md"
    sub_tasks: ["User stories", "Data model", "User flows"]
    delegate_to: "prd-builder"  # if available
```

**Flow patterns:**
```yaml
flows:
  dev:   [analyze, design, implement, test, review]
  arch:  [research, evaluate, decide, document, validate]
  deploy: [build, test, stage, verify, deploy]
```

**Multi-flow** — parallel execution for independent tasks:
```yaml
multi_flow:
  - parallel: [T-005, T-006, T-007]  # Auth + CRUD + API in parallel
    sync_gate: "All integrated and tested"
```

### A3. PLAN — Present Mission Briefing

Show the user the full plan before executing:

```
# Mission Briefing: {Goal}

## Phase 1: Foundation (Week 1-2)
Artifacts: 📄 PRD │ 📐 Architecture │ 📊 Data Model │ 🏗️ Scaffold
Tasks: T-001 → T-002 → T-003 → T-004
Gate: ✅ Architecture validated

## Phase 2: Core MVP (Week 3-4)
Artifacts: 🔐 Auth │ 📝 CRUD │ 🎨 UI │ 💾 Database
Tasks: T-005 ═╦═ T-006 ═╦═ T-007 → T-008
              ║ parallel ║
Gate: ✅ Core flow working end-to-end

## Phase 3: Launch (Week 5-6)
Artifacts: 💳 Payments │ 🧪 Tests │ 🌐 Landing │ 🚀 Deploy
Gate: ✅ Live and monitored
```

Wait for user approval or modifications before executing.

### A4. EXECUTE — Run With Quality Gates

Execute each task, producing artifacts. At each gate:

```
GATE: {Name}
├─ ✅ Artifacts produced?
├─ ✅ Quality criteria met?
├─ ✅ Dependencies satisfied?
└─ ✅ User validated?
→ PASS / PARTIAL / FAIL
```

**Execution rules:**
1. Every task produces a tangible artifact (file, not just text)
2. Delegate to specialized skills when available (see integration map below)
3. Show progress after each task
4. At Phase 1 completion → auto-trigger **MODE B** to install agent skills

### A5. DELIVER — Artifacts Catalog

Standard output structure:
```
docs/prd.md, architecture.md, data-model.md, user-stories.md, adr/
src/ (project code)
tests/ (test suite)
deploy/ (Dockerfile, CI/CD)
.agents/skills/ (agent skills — from Mode B)
```

### Adaptive Complexity

| Complexity | Behavior |
|-----------|----------|
| 1-3 (Simple) | Skip missions. Goal → 3-5 tasks → deliver |
| 4-6 (Medium) | 1-2 missions, sequential flow |
| 7-10 (Complex) | 3 missions, multi-flow, strict gates |

---

## MODE B: AGENT SKILL SYSTEM

### B1. DETECT — Project Stack + Agents

Scan for dependency manifests: `package.json`, `requirements.txt`, `Cargo.toml`,
`go.mod`, `Gemfile`, `composer.json`, `pubspec.yaml`, `build.gradle`, `*.csproj`.

Scan for installed AI agents by checking home directories. See
`references/agents-full-list.md` for the complete 39-agent mapping.

### B2. FETCH — Search & Download

Priority: llms.txt Hub registry → project `/llms.txt` → GitHub → generate from docs.

Use `npx llmstxt-cli install <n>` when available, or `scripts/install_skills.sh`.

### B3. GENERATE — Produce llms.txt & SKILL.md

From project docs, generate:
- `llms.txt` — concise index (llmstxt.org spec, see `references/llmstxt-spec.md`)
- `llms-full.txt` — complete docs (<500KB)
- `SKILL.md` — agent-ready with YAML frontmatter (description ≤1024 chars)

Use `scripts/generate_llmstxt.py` for automated generation.

### B4. OPTIMIZE — Agent-Native Adaptation

Each agent reads skills differently. Adapt using profiles from
`references/agent-native-profiles.md` (derived from 32 system prompts):

| Agent | Style | Max Lines | Key Convention |
|-------|-------|-----------|----------------|
| Claude Code | Reasoning + examples | 500 | YAML frontmatter, explain WHY |
| Cursor | Dense imperative | 200 | Front-load patterns, code > prose |
| Windsurf | Workflow steps | 400 | Numbered steps, cascade pattern |
| Cline/Roo | Tool-use procedural | 400 | Tool call examples, decision trees |
| Copilot | Example-heavy | 300 | Code patterns, signatures |
| Universal | Clean markdown | 400 | No custom tags, portable |

Use `scripts/optimize_for_agent.py --agent {name}` for per-agent optimization.

### B5. INSTALL — Multi-Agent Distribution

```
.agents/skills/{name}/SKILL.md    ← canonical
.claude/skills/{name} → symlink
.cursor/skills/{name} → symlink
.windsurf/skills/{name} → symlink
... (39 agent directories)
```

Update config files: `CLAUDE.md`, `.cursorrules`, `.windsurfrules`.

---

## Skill Integration Map

NEXUS orchestrates all available skills:

| Need | Delegate To | Fallback |
|------|------------|----------|
| Full context | `context-builder` | Inline |
| PRD | `prd-builder` | `context-builder` |
| Architecture | `agent-architecture-builder` | Inline |
| Multi-agent | `numtema-universal-framework` | Inline |
| Workflows | `numflow-llm` | Inline |
| Next.js scaffold | `bun-nextjs-starter` | Manual |
| Agent skills | `llmstxt-skill-installer` | Mode B inline |
| Deep reasoning | `morphosys-cognitive-engine` | Standard |
| Prompts | `vortex-meta-prompt-engineer` | Inline |
| Documents | `docx`, `pptx`, `xlsx`, `pdf` skills | Markdown |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/install_skills.sh` | Standalone skill installer (no npm) |
| `scripts/generate_llmstxt.py` | Generate llms.txt / SKILL.md from docs |
| `scripts/optimize_for_agent.py` | Adapt SKILL.md per agent profile |

---

## Key Principles

1. **Plan before code** — Mission briefing comes first, always
2. **Every task → artifact** — No task completes without a tangible output
3. **Gates prevent drift** — Validate before advancing to next phase
4. **Agent-native skills** — Optimize for each agent's internal conventions
5. **Delegate to specialists** — Use other skills when they exist
6. **Adapt to complexity** — Simple idea? Light plan. Complex SaaS? Full hierarchy.
7. **User controls everything** — The plan is a proposal, not a mandate
