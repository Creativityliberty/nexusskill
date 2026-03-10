# Nanoclaw Forge — Full Pipeline Example

## Command

```bash
python scripts/forge_bridge.py "Build a SaaS customer support chatbot" \
  --constraints "3 months, 2 developers, $20k" \
  --domain auto \
  --mode single \
  --output ./chatbot_forge
```

## What Happens

### Phase 1: PLAN

```
🏗️ PHASE 1: PLAN (blueprint-maker)
🔍 Auto-detected domain: product
✅ Blueprint: 12 sections
📄 Saved to: chatbot_forge/blueprint.md
```

Blueprint includes:

- Executive Summary
- Objectives  
- User Personas (auto-generated for "product" domain)
- Feature Matrix
- Tech Stack recommendation
- Timeline & Milestones
- Risks & Mitigations

### Phase 2: MAP

```
🌲 PHASE 2: MAP (dag-taskview)
✅ DAG: 12 tasks
🔥 Critical path: 8 steps

Mermaid diagram with:
- ✅ Done (green)
- 🔄 In Progress (yellow)  
- ⏳ Pending (gray)
- 🚫 Blocked (red)
```

### Phase 3: BUILD

```
⚙️ PHASE 3: BUILD (orchestra-forge)
✅ agent.yaml: 12 nodes
✅ agent.py: PocketFlow implementation
```

Generated files:

- `agent.yaml` — Nüm Agents spec with PocketFlowCore + StructureAgentIA
- `agent.py` — 12 PocketFlow Node classes, wired flow

### Phase 4: RUN

```
⚡ PHASE 4: RUN (flow-orchestrator)
✅ Run config generated
💡 Execute: python chatbot_forge/agent.py
```

### Phase 5: SHIP

```
📦 PHASE 5: SHIP (artifact-maker + skill-architect)
📦 [MARKDOWN] blueprint.md (4.2KB)
📦 [PDF] blueprint.pdf (128KB)
📦 [CHART] dag.html (2.1KB)
📦 [CODE] agent.py (3.8KB)
📦 [YAML] agent.yaml (1.2KB)
📦 [JSON] pipeline_state.json (0.3KB)
📋 Manifest: 6 artifacts
```

## Output Directory

```
chatbot_forge/
├── blueprint.md          ← Full project blueprint
├── dag.md                ← Mermaid DAG diagram
├── agent.yaml            ← Nüm Agents spec
├── agent.py              ← PocketFlow implementation
├── run_config.json       ← Execution configuration
└── artifacts/
    ├── blueprint.md
    ├── blueprint.pdf
    ├── dag.html
    ├── agent.py
    ├── agent.yaml
    ├── pipeline_state.json
    └── manifest.json
```

## Phase Selection

Run only specific phases:

```bash
# Just plan
python scripts/forge_bridge.py "Build a chatbot" --phases plan

# Plan + Map
python scripts/forge_bridge.py "Build a chatbot" --phases plan,map

# Skip to build (requires existing state)
python scripts/forge_bridge.py "Build a chatbot" --phases build,run,ship
```
