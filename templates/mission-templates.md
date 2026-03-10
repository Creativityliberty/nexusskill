# Mission Templates

Pre-built mission structures for common project types. The orchestrator selects
the best template based on user intent, then customizes it.

---

## Template: SaaS Application

```yaml
goal:
  type: saas
  default_stack: "Next.js + Supabase + Vercel + Stripe"
  default_timeline: "6 weeks"

missions:
  - id: M-001
    title: "Discovery & Architecture"
    phase: 1
    duration: "1-2 weeks"
    tasks:
      - title: "Product Requirements Document"
        artifact: "docs/prd.md"
        delegate_to: "prd-builder"
      - title: "User Stories & Personas"
        artifact: "docs/user-stories.md"
      - title: "Architecture Decision Records"
        artifact: "docs/adr/"
        delegate_to: "context-builder"
      - title: "Data Model & Schema"
        artifact: "docs/data-model.md"
      - title: "API Design"
        artifact: "docs/api-spec.yaml"
      - title: "Project Scaffold"
        artifact: "/ (project root)"
        delegate_to: "bun-nextjs-starter"
    gate: "PRD approved, architecture validated, scaffold running"

  - id: M-002
    title: "Core MVP Build"
    phase: 2
    duration: "2-3 weeks"
    tasks:
      - title: "Authentication System"
        sub_tasks: ["OAuth/Magic Link setup", "User profile CRUD", "Role-based access"]
      - title: "Core Business Logic"
        sub_tasks: ["Primary CRUD operations", "Business rules engine", "Validation"]
      - title: "Database & API Layer"
        sub_tasks: ["Schema migration", "API endpoints", "Data validation"]
      - title: "UI/UX Implementation"
        sub_tasks: ["Layout & navigation", "Core screens", "Responsive design"]
    gate: "Core features working end-to-end with test data"

  - id: M-003
    title: "Polish, Payments & Launch"
    phase: 3
    duration: "1-2 weeks"
    tasks:
      - title: "Payment Integration"
        sub_tasks: ["Stripe setup", "Subscription plans", "Billing portal"]
      - title: "Testing & QA"
        sub_tasks: ["Unit tests", "Integration tests", "Manual QA"]
      - title: "Landing Page"
        artifact: "landing/ or public/"
      - title: "Deployment & Monitoring"
        sub_tasks: ["CI/CD pipeline", "Production deploy", "Error tracking"]
      - title: "Documentation"
        artifact: "docs/README.md"
    gate: "Deployed, payments working, landing page live"
```

---

## Template: API / Backend Service

```yaml
goal:
  type: api
  default_stack: "FastAPI + PostgreSQL + Docker"
  default_timeline: "3-4 weeks"

missions:
  - id: M-001
    title: "Design & Specification"
    phase: 1
    tasks:
      - title: "API Specification (OpenAPI)"
        artifact: "docs/openapi.yaml"
      - title: "Data Model"
        artifact: "docs/data-model.md"
      - title: "Authentication Strategy"
        artifact: "docs/adr/001-auth.md"
      - title: "Project Scaffold"
        artifact: "/ (project root)"
    gate: "API spec reviewed, data model validated"

  - id: M-002
    title: "Implementation"
    phase: 2
    tasks:
      - title: "Database Layer"
        sub_tasks: ["Models", "Migrations", "Seed data"]
      - title: "API Endpoints"
        sub_tasks: ["CRUD routes", "Business logic", "Validation"]
      - title: "Authentication"
        sub_tasks: ["JWT/OAuth", "Middleware", "Rate limiting"]
      - title: "Integration Tests"
        artifact: "tests/"
    gate: "All endpoints working, tests passing"

  - id: M-003
    title: "Deploy & Document"
    phase: 3
    tasks:
      - title: "Docker Configuration"
        artifact: "Dockerfile + docker-compose.yml"
      - title: "CI/CD Pipeline"
        artifact: ".github/workflows/"
      - title: "API Documentation"
        artifact: "docs/ + Swagger UI"
      - title: "Deploy to Production"
    gate: "Deployed, documented, health checks passing"
```

---

## Template: CLI Tool

```yaml
goal:
  type: cli
  default_stack: "Node.js (Commander) or Python (Click/Typer)"
  default_timeline: "2-3 weeks"

missions:
  - id: M-001
    title: "Design"
    phase: 1
    tasks:
      - title: "Command Structure"
        artifact: "docs/commands.md"
      - title: "Project Scaffold"
    gate: "Commands defined, scaffold working"

  - id: M-002
    title: "Build"
    phase: 2
    tasks:
      - title: "Core Commands"
      - title: "Configuration System"
      - title: "Error Handling & Help"
      - title: "Tests"
    gate: "All commands working, tests passing"

  - id: M-003
    title: "Package & Publish"
    phase: 3
    tasks:
      - title: "Package for Distribution"
        artifact: "package.json or setup.py"
      - title: "README & Docs"
      - title: "Publish to Registry"
    gate: "Published, installable, documented"
```

---

## Template: Multi-Agent System

```yaml
goal:
  type: multi_agent
  default_stack: "Python + FastAPI + MCP"
  default_timeline: "4-6 weeks"

missions:
  - id: M-001
    title: "Agent Architecture"
    phase: 1
    tasks:
      - title: "Agent Roles & Responsibilities"
        artifact: "docs/agents.md"
        delegate_to: "numtema-universal-framework"
      - title: "Communication Protocol"
        artifact: "docs/protocol.md"
      - title: "Tool Definitions (MCP)"
        artifact: "docs/tools.md"
      - title: "Scaffold"
        delegate_to: "agent-architecture-builder"
    gate: "Architecture validated, scaffold running"

  - id: M-002
    title: "Agent Implementation"
    phase: 2
    tasks:
      - title: "Core Agent Logic"
      - title: "MCP Server Setup"
      - title: "Inter-Agent Communication"
      - title: "Tool Implementation"
    gate: "Agents communicating, tools working"

  - id: M-003
    title: "Orchestration & Deploy"
    phase: 3
    tasks:
      - title: "Orchestrator / Router"
      - title: "Testing & Evaluation"
      - title: "Deployment"
      - title: "Monitoring"
    gate: "System running in production"
```

---

## Template: Automation / Internal Tool

```yaml
goal:
  type: automation
  default_stack: "Python + Cron/Celery or Node.js"
  default_timeline: "1-2 weeks"

missions:
  - id: M-001
    title: "Design & Build"
    phase: 1
    tasks:
      - title: "Requirements"
        artifact: "docs/requirements.md"
      - title: "Implementation"
      - title: "Testing"
    gate: "Working locally, tested"

  - id: M-002
    title: "Deploy & Monitor"
    phase: 2
    tasks:
      - title: "Scheduling / Triggers"
      - title: "Error Handling & Alerts"
      - title: "Deploy"
    gate: "Running in production, monitored"
```

---

## Template Selection Logic

Match user intent to template:

| Keywords | Template |
|----------|----------|
| saas, platform, subscription, billing, users, dashboard | SaaS Application |
| api, backend, service, endpoint, server, microservice | API / Backend |
| cli, command, terminal, tool, script | CLI Tool |
| agent, multi-agent, mcp, orchestration, ai system | Multi-Agent System |
| automate, cron, pipeline, workflow, internal tool, script | Automation |

If unclear, default to **SaaS Application** (most comprehensive) and adapt.
