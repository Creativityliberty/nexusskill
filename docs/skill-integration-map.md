# Skill Integration Map

How the Mission Orchestrator delegates work to specialized skills.
The orchestrator checks which skills are available and routes tasks accordingly.

---

## Delegation Matrix

| Task Type | Primary Skill | Fallback | What It Produces |
|-----------|--------------|----------|------------------|
| Full project context | `context-builder` | Inline generation | Brief, PRD, backlog, ADR, data model, CI/CD |
| PRD document | `prd-builder` | `context-builder` → Inline | Comprehensive requirements doc |
| PRD with RRLA reasoning | `numtema-prd-pro` | `prd-builder` | PRD with formal reasoning traces |
| Architecture design | `agent-architecture-builder` | Inline | Full-stack architecture + code |
| Multi-agent system | `numtema-universal-framework` | `agent-architecture-builder` | Agent network + orchestration |
| Agent scaffolding | `ai-agent-scaffolder` | `agent-architecture-builder` | Agent project with MCP, RRLA |
| Google ADK agents | `google-adk-builder` | `ai-agent-scaffolder` | Google ADK agent code |
| Workflow phases | `numflow-llm` | Inline | Structured phases + quality gates |
| Workflow orchestration | `workflow-orchestrator` | `numflow-llm` | Intent-driven workflow execution |
| Next.js scaffold | `bun-nextjs-starter` | Manual scaffold | Working Next.js + Bun project |
| Deep analysis | `morphosys-cognitive-engine` | Standard reasoning | Thorough multi-angle analysis |
| Prompt engineering | `vortex-meta-prompt-engineer-v2` | v1 → Inline | Production-ready prompts |
| Business idea scoring | `vortex-numos` | Inline analysis | Scored and validated idea |
| Agent skills setup | `llmstxt-skill-installer` | Manual setup | Skills installed for all agents |
| Developer learning path | `developer-roadmap` | N/A | Skills roadmap |
| RAG chatbot | `gemini-rag-chatbot` | N/A | RAG system with Gemini |
| BMAD agents | `bmad-integration` | N/A | BMAD agent system |
| Document creation | `docx` skill | Markdown | Word documents |
| Presentations | `pptx` skill | N/A | PowerPoint slides |
| Spreadsheets | `xlsx` skill | CSV | Excel files |
| PDFs | `pdf` skill | N/A | PDF documents |
| Skill Creation | `skill-creator` | `skill-architect` | New SKILL.md for agents |
| Blueprinting | `blueprint-maker` | `artifact-maker` | Project blueprints / specs |
| PR Review | `review-pr` | Standard analysis | PR feedback and audit |
| UI Steaming | `ui-style-generator` | Standard CSS | Premium UI styles |
| GitHub Commits | `commit` | Standard git | Semantic commit messages |
| Workspace Hooks | `session-start-hook` | N/A | Automated session init |
| Task Analysis | `morsel-tasks` | `task-tree` | Decomposed task hierarchy |

---

## Delegation Protocol

### Step 1: Check Availability

Before delegating, verify the skill exists:

```python
# Conceptual — the LLM checks its available_skills list
if skill_available("context-builder"):
    delegate_to("context-builder", task_params)
elif skill_available("prd-builder"):
    delegate_to("prd-builder", task_params)
else:
    execute_inline(task_params)
```

### Step 2: Prepare Context

When delegating, provide the skill with:
- The specific task description
- Relevant context from the mission plan
- Expected artifact format and location
- Any constraints from the goal definition

### Step 3: Integrate Results

After a skill produces output:
- Verify the artifact meets quality gate criteria
- Place artifact in the correct location
- Update the mission progress tracker
- Proceed to next task

---

## Skill Chaining Patterns

### Pattern 1: Discovery → Architecture → Build

```
context-builder → agent-architecture-builder → bun-nextjs-starter
     ↓                      ↓                         ↓
  PRD + Backlog      Architecture docs          Working scaffold
```

### Pattern 2: Idea → Validation → Mission

```
vortex-numos → morphosys-cognitive-engine → mission-orchestrator
     ↓                    ↓                        ↓
  Scored idea      Deep analysis           Full mission plan
```

### Pattern 3: PRD → Flow → Execution

```
numtema-prd-pro → numflow-llm → workflow-orchestrator
       ↓                ↓                ↓
   Formal PRD     Phase plan       Executed workflow
```

### Pattern 4: Full Stack Agent

```
numtema-universal-framework → google-adk-builder → llmstxt-skill-installer
            ↓                         ↓                      ↓
     Agent architecture        ADK agent code         Skills for all agents
```

---

## When NOT to Delegate

Handle directly (no delegation needed) when:
- Task is simple enough to do inline (< 5 minutes of work)
- The specialized skill would add overhead without value
- User explicitly wants a specific approach
- The task is highly custom and no template fits

---

## Integration with External Tools (MCP)

When MCP connectors are available, the orchestrator can also delegate to:

| MCP Server | Use Case |
|-----------|----------|
| Google Calendar | Schedule milestones and deadlines |
| Gmail | Send project updates |
| Canva | Create visual assets |
| Vercel | Deploy frontend |
| Netlify | Deploy static sites |
| Cloudflare | Configure infrastructure |
| Sentry | Set up error tracking |
| Mermaid Chart | Generate architecture diagrams |
