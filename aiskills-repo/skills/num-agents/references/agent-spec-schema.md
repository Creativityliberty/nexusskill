# Agent Spec Schema (YAML)

Schema for `agent.yaml` — the input to `num-agents generate`.

## Full Schema

```yaml
agent:
  # Required
  name: string              # PascalCase agent name (e.g. "SummaryAgent")
  description: string       # One-line description of what the agent does

  # Universes — functional modules to activate (required, min 1)
  # See universe-catalog.md for all available values
  univers:
    - PocketFlowCore        # always include this as the base
    - StructureAgentIA      # optional: structured LLM outputs
    - KnowledgeLayer        # optional: memory + retrieval
    - ConditionalFlow       # optional: if/else branching
    - EventBusUnivers       # optional: inter-agent messaging
    - SchedulerUnivers      # optional: cron scheduling
    - APIConnectorUnivers   # optional: external HTTP calls
    - RAGUnivers            # optional: full RAG pipeline

  # Protocol
  protocol: N2A             # N2A (Node-to-Agent) | A2A (Agent-to-Agent)

  # LLM backend
  llm: claude-sonnet-4-6   # any LiteLLM-compatible model string

  # Optional features (default: false)
  memory: false             # enable persistent conversation memory
  eventbus: false           # enable pub/sub event bus
  scheduler: false          # enable task scheduler
  metrics: false            # enable performance metrics
  tracing: false            # enable distributed tracing
```

## Minimal Spec

```yaml
agent:
  name: "FetchSummarizeAgent"
  description: "Fetches a URL and summarizes the content"
  univers:
    - PocketFlowCore
  protocol: N2A
  llm: claude-sonnet-4-6
```

## Knowledge Agent

```yaml
agent:
  name: "DocQAAgent"
  description: "Answers questions from a document knowledge base"
  univers:
    - PocketFlowCore
    - StructureAgentIA
    - KnowledgeLayer
    - RAGUnivers
  protocol: N2A
  llm: claude-sonnet-4-6
  memory: true
  metrics: true
  tracing: true
```

## Multi-Agent Orchestrator

```yaml
agent:
  name: "OrchestratorAgent"
  description: "Routes tasks to specialized sub-agents via event bus"
  univers:
    - PocketFlowCore
    - StructureAgentIA
    - ConditionalFlow
    - EventBusUnivers
    - APIConnectorUnivers
  protocol: A2A
  llm: claude-sonnet-4-6
  eventbus: true
  metrics: true
  tracing: true
```

## Code Review Agent

```yaml
agent:
  name: "CodeReviewAgent"
  description: "Reviews code changes, runs static analysis, posts PR comments"
  univers:
    - PocketFlowCore
    - StructureAgentIA
    - ConditionalFlow
    - APIConnectorUnivers
  protocol: N2A
  llm: claude-sonnet-4-6
  metrics: true
  tracing: true
```

## Scheduled Report Agent

```yaml
agent:
  name: "WeeklyReportAgent"
  description: "Generates and sends weekly analytics reports on schedule"
  univers:
    - PocketFlowCore
    - StructureAgentIA
    - KnowledgeLayer
    - SchedulerUnivers
    - APIConnectorUnivers
  protocol: N2A
  llm: claude-sonnet-4-6
  scheduler: true
  memory: true
  metrics: true
```

## CLI Usage

```bash
# Generate from spec
num-agents generate --spec agent.yaml

# With custom universe catalog
num-agents generate --spec agent.yaml --catalog univers_catalog.yaml

# Generate and output to a specific directory
num-agents generate --spec agent.yaml --output ./my_agent/

# Validate spec only (no generation)
num-agents validate --spec agent.yaml
```

## Generated Project Structure

After running `num-agents generate`, you get:

```
my_agent/
├── agent.py            ← main agent entry point
├── nodes/
│   └── __init__.py     ← scaffolded Node classes (one per step)
├── flows/
│   └── pipeline.py     ← wired Flow definition
├── config/
│   └── settings.py     ← LLM + universe config
└── tests/
    └── test_agent.py   ← basic test scaffold
```
