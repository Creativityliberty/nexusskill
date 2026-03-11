# Plan — Workflow + TaskTree + Morsel + Artifacts System

## Vision

Un système en 4 skills interconnectés qui permettent d'orchestrer n'importe quel goal complexe
en pipelines de skills existants, avec décomposition en tâches atomiques et production d'artifacts.

```
GOAL
  ↓ [task-tree]      Décompose en arbre hiérarchique de tâches
  ↓ [workflow]       Orchestre: quel skill pour quelle tâche, dans quel ordre
  ↓ [morsel-tasks]   Exécute chaque tâche atomique (avec retry/checkpoint)
  ↓ [artifacts-maker] Collecte et organise les outputs produits
```

---

## 4 Skills à créer

### 1. `task-tree`
**Rôle**: Décomposer un goal complexe en arbre de tâches hiérarchiques.

Structure produite:
```yaml
goal: "Build a complete MVP for a fintech dashboard"
tasks:
  - id: t1
    name: "Generate design system"
    skill: ui-style-generator
    input: { prompt: "fintech dashboard, dark minimal" }
    output_artifact: styleguide.md
    depends_on: []

  - id: t2
    name: "Setup project structure"
    skill: null   # Claude fait directement
    depends_on: []
    parallel_with: [t1]

  - id: t3
    name: "Commit initial files"
    skill: commit
    depends_on: [t1, t2]
    output_artifact: commit-hash.txt
```

Bundled:
- `scripts/task_tree.py` — CLI: goal → task tree YAML + visual ASCII tree
- `references/decomposition-strategies.md` — patterns par type de goal

---

### 2. `workflow`
**Rôle**: Orchestrateur principal. Lit un task tree YAML, exécute chaque skill en séquence/parallèle/conditionnel, passe les outputs d'un skill en input du suivant.

Workflow YAML format:
```yaml
workflow:
  name: "MVP Builder"
  version: "1.0"
  steps:
    - id: step1
      skill: ui-style-generator
      input:
        prompt: "{{ goal.description }}"
      output: styleguide

    - id: step2
      depends_on: [step1]
      skill: commit
      input:
        files: ["{{ styleguide.path }}"]

    - id: step3
      condition: "{{ step2.exit_code == 0 }}"
      skill: review-pr
```

Bundled:
- `scripts/workflow_engine.py` — parse YAML + run pipeline + track state
- `references/pipeline-patterns.md` — sequential, parallel, conditional, fan-out/fan-in
- `references/skill-registry.md` — index de tous les skills + leurs I/O contracts

---

### 3. `morsel-tasks`
**Rôle**: Système d'exécution atomique. Chaque "morsel" = la plus petite unité de travail indivisible. Supporte: checkpoint (reprendre où on s'était arrêté), retry, skip, validation.

Morsel format:
```yaml
morsel:
  id: m1
  task_ref: t1
  action: "call skill ui-style-generator with prompt=..."
  expected_output: "a STYLEGUIDE.md file"
  validate: "file STYLEGUIDE.md exists AND has > 100 lines"
  on_fail: retry(max=3) | skip | escalate
  checkpoint_after: true
```

Checkpoint system:
- Sauvegarde l'état dans `.workflow/checkpoint.json`
- Si interrupted → reprend depuis le dernier morsel complété
- Chaque morsel marqué: `pending | running | done | failed | skipped`

Bundled:
- `scripts/morsel_runner.py` — exécute morsels + gère checkpoints
- `references/morsel-patterns.md` — atomic patterns par type d'action

---

### 4. `artifacts-maker`
**Rôle**: Chaque morsel complété produit un artifact. Ce skill collecte, nomme, organise et crée un manifeste de tous les outputs.

Output structure:
```
artifacts/
├── manifest.json          ← index de tous les artifacts
├── 001_styleguide.md      ← préfixé par ordre d'exécution
├── 002_commit-hash.txt
├── 003_pr-review.md
└── 004_deployment-config.yaml
```

manifest.json:
```json
[
  {
    "id": "001",
    "name": "styleguide.md",
    "type": "markdown",
    "source_task": "t1",
    "source_skill": "ui-style-generator",
    "path": "artifacts/001_styleguide.md",
    "size_bytes": 4821,
    "created_at": "2026-02-21T10:30:00Z"
  }
]
```

Artifact types: `code`, `markdown`, `json`, `config`, `image`, `report`, `diff`, `commit`

Bundled:
- `scripts/artifact_registry.py` — collecte + manifeste
- `references/artifact-types.md` — types + conventions de nommage

---

## Architecture globale

```
skills/
├── task-tree/
│   ├── SKILL.md
│   ├── scripts/task_tree.py
│   └── references/decomposition-strategies.md
│
├── workflow/
│   ├── SKILL.md
│   ├── scripts/workflow_engine.py
│   └── references/
│       ├── pipeline-patterns.md
│       └── skill-registry.md          ← auto-généré depuis le repo
│
├── morsel-tasks/
│   ├── SKILL.md
│   ├── scripts/morsel_runner.py
│   └── references/morsel-patterns.md
│
└── artifacts-maker/
    ├── SKILL.md
    ├── scripts/artifact_registry.py
    └── references/artifact-types.md
```

## Dépendances entre skills

```
workflow  →  task-tree       (utilise le tree pour planifier)
workflow  →  morsel-tasks    (délègue l'exécution atomique)
workflow  →  artifacts-maker (collecte les outputs)
morsel-tasks → artifacts-maker (chaque morsel produit un artifact)
task-tree  →  [tous les autres skills] (chaque tâche invoque un skill)
```

## Utilisation finale

```
User: "Build a complete MVP landing page for my fintech app"

Claude:
1. [task-tree]      → décompose en 8 tâches
2. [workflow]       → crée le pipeline YAML
3. [morsel-tasks]   → exécute tâche par tâche avec checkpoint
   - Morsel 1: ui-style-generator → styleguide.md ✅
   - Morsel 2: Create HTML structure → index.html ✅
   - Morsel 3: commit → hash abc123 ✅
   ...
4. [artifacts-maker] → organise dans artifacts/ + manifest.json

Result: artifacts/ avec tous les fichiers produits + manifeste
```

## Fichiers à créer (15 fichiers)

| Fichier | Priorité |
|---------|----------|
| skills/task-tree/SKILL.md | haute |
| skills/task-tree/scripts/task_tree.py | haute |
| skills/task-tree/references/decomposition-strategies.md | haute |
| skills/workflow/SKILL.md | haute |
| skills/workflow/scripts/workflow_engine.py | haute |
| skills/workflow/references/pipeline-patterns.md | haute |
| skills/workflow/references/skill-registry.md | haute |
| skills/morsel-tasks/SKILL.md | haute |
| skills/morsel-tasks/scripts/morsel_runner.py | haute |
| skills/morsel-tasks/references/morsel-patterns.md | moyenne |
| skills/artifacts-maker/SKILL.md | haute |
| skills/artifacts-maker/scripts/artifact_registry.py | haute |
| skills/artifacts-maker/references/artifact-types.md | moyenne |
| README.md update | basse |
| commit + push | — |
