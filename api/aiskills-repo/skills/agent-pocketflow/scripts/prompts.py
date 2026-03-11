"""
Prompt Templates — Structured prompts for each document type.

Each prompt is a template string with placeholders for context data.
Used by LLMNode and DocUpdateNode to generate content.
"""

# ---------- DM-Log ----------
DM_LOG_PROMPT = """
Tu es un assistant spécialisé dans la documentation de projets de développement logiciel.
Génère une entrée pour un journal DM-Log au format Markdown.

## Informations
- Tâche: {task_name}
- Date: {today}
- Résultats: {task_results}
- Prochaines étapes: {next_steps}
- Contenu actuel: {current_content}

## Instructions
1. Génère une nouvelle entrée avec: titre + date, tâches accomplies, résultats, prochaines étapes
2. Ton professionnel et concis
3. Ne répète pas les entrées existantes
4. Format Markdown uniquement

Génère uniquement l'entrée, sans explications.
"""

# ---------- MCD ----------
MCD_PROMPT = """
Le document suivant définit le Modèle Conceptuel de Données et les Garde-fous techniques.
Mets-le à jour en ajoutant ou corrigeant les sections selon les dernières modifications du projet.

```markdown
{content}
```

RENVOIE le document complet en Markdown valide.
"""

# ---------- Project Structure ----------
PROJECT_STRUCTURE_PROMPT = """
Le document suivant décrit la structure du projet.
Mets-le à jour pour refléter les dernières conventions et scripts d'automatisation.

```markdown
{content}
```

RENVOIE le document complet en Markdown valide.
"""

# ---------- Tasks ----------
TASKS_PROMPT = """
Le document suivant décrit les tâches du projet.
Mets-le à jour pour refléter l'avancement et les nouvelles tâches.

```markdown
{content}
```

RENVOIE le document complet en Markdown valide.
"""

# ---------- Requirements ----------
REQUIREMENTS_PROMPT = """
Le document suivant décrit les exigences du projet.
Mets-le à jour pour refléter les nouvelles exigences et les modifications.

```markdown
{content}
```

RENVOIE le document complet en Markdown valide.
"""

# ---------- Dashboard ----------
DASHBOARD_PROMPT = """
Génère un dashboard ASCII pour un flow PocketFlow.

- Nom: {flow_name}
- État: {flow_status}
- Progression: {completed_nodes}/{total_nodes}
- Nodes terminés: {completed_node_names}
- Node en cours: {current_node}
- Erreurs: {errors}
- Temps: {elapsed_time}

Dashboard ASCII avec barre de progression, statut par node, et résumé.
Largeur max: 80 caractères.
"""
