# Universe Catalog

## Table of Contents
1. [Core Universes](#core-universes)
2. [Knowledge & Memory](#knowledge--memory)
3. [Infrastructure](#infrastructure)
4. [Observability](#observability)
5. [How to Choose](#how-to-choose)

---

## Core Universes

### `PocketFlowCore`
**Purpose**: Node/Flow execution engine (based on PocketFlow pattern)
**Provides**: `Node`, `Flow`, `BatchNode`, `AsyncNode`, `AsyncFlow`, `SharedStore`
**Use when**: Any agent that needs multi-step execution, retry logic, or async processing

```yaml
univers:
  - PocketFlowCore
```

### `StructureAgentIA`
**Purpose**: Structured reasoning and output generation
**Provides**: Typed output schemas, chain-of-thought templates, structured LLM calls
**Use when**: Agent needs to produce structured JSON outputs or follow reasoning steps

```yaml
univers:
  - StructureAgentIA
```

### `ConditionalFlow`
**Purpose**: Conditional branching and decision trees in flows
**Provides**: `ConditionalNode`, `BranchNode`, `RouterNode`
**Use when**: Agent needs to make decisions and route to different nodes

```yaml
univers:
  - ConditionalFlow
```

---

## Knowledge & Memory

### `KnowledgeLayer`
**Purpose**: Retrieval-augmented memory and document storage
**Provides**: Vector store integration, semantic search, conversation memory
**Use when**: Agent needs to remember past interactions or search a knowledge base

```yaml
univers:
  - KnowledgeLayer
memory: true
```

### `RAGUnivers`
**Purpose**: Full RAG pipeline (ingest → chunk → embed → retrieve → generate)
**Provides**: Document loaders, chunking strategies, embedding models
**Use when**: Agent needs to answer questions from a document corpus

---

## Infrastructure

### `EventBusUnivers`
**Purpose**: Pub/sub event system between agents
**Provides**: Event emitter, subscriber registry, async message passing
**Use when**: Multi-agent system where agents need to communicate

```yaml
univers:
  - EventBusUnivers
eventbus: true
```

### `SchedulerUnivers`
**Purpose**: Cron-like task scheduling for agents
**Provides**: Job scheduler, cron expressions, delayed execution
**Use when**: Agent needs to run on a schedule (e.g. daily report, polling)

```yaml
univers:
  - SchedulerUnivers
scheduler: true
```

### `APIConnectorUnivers`
**Purpose**: HTTP/REST API integration with retry and auth
**Provides**: HTTP client with exponential backoff, OAuth helper, rate limiter
**Use when**: Agent makes external API calls

---

## Observability

### `MetricsUnivers`
**Purpose**: Performance and execution metrics
**Provides**: Counters, histograms, latency tracking per node
**Use when**: Production agents where you need to monitor performance

```yaml
metrics: true
```

### `TracingUnivers`
**Purpose**: Distributed tracing across agent flows
**Provides**: OpenTelemetry-compatible spans, trace IDs, context propagation
**Use when**: Multi-agent systems, debugging complex flows

```yaml
tracing: true
```

---

## How to Choose

| I need... | Use |
|-----------|-----|
| Basic multi-step execution | `PocketFlowCore` |
| Structured LLM outputs | `StructureAgentIA` |
| If/else branching | `ConditionalFlow` |
| Remember conversations | `KnowledgeLayer` + `memory: true` |
| Search documents | `RAGUnivers` |
| Agents talking to each other | `EventBusUnivers` |
| Run on a cron schedule | `SchedulerUnivers` |
| Call external APIs | `APIConnectorUnivers` |
| Monitor in production | `MetricsUnivers` + `TracingUnivers` |

### Minimal Agent (just execution)
```yaml
univers:
  - PocketFlowCore
```

### Knowledge Agent
```yaml
univers:
  - PocketFlowCore
  - StructureAgentIA
  - KnowledgeLayer
memory: true
```

### Production Multi-Agent
```yaml
univers:
  - PocketFlowCore
  - StructureAgentIA
  - KnowledgeLayer
  - EventBusUnivers
  - APIConnectorUnivers
memory: true
eventbus: true
metrics: true
tracing: true
```
