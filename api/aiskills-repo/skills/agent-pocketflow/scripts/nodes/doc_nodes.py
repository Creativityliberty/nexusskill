"""
Doc Nodes — Nodes for document auto-update.

Each node reads a doc file, calls LLM to update it, and writes it back.
Nodes: DMLogParserNode, DMLogLLMNode, DMLogUpdateNode,
       ModelConceptUpdateNode, ProjectStructureUpdateNode,
       TasksUpdateNode, RequirementsUpdateNode
"""

import os
from nodes.base_node import BaseNode
from nodes.llm_node import LLMNode
from prompts import (
    DM_LOG_PROMPT, MCD_PROMPT, PROJECT_STRUCTURE_PROMPT,
    TASKS_PROMPT, REQUIREMENTS_PROMPT
)


class DMLogParserNode(BaseNode):
    """Reads and parses the DM-Log journal."""

    def __init__(self, path="docs/dm-log.md"):
        super().__init__("dm_log_parser")
        self.path = path

    def exec(self, context):
        if os.path.exists(self.path):
            with open(self.path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = "# DM-Log\n\n## Résultats des étapes\n"
        context["dm_content"] = content
        return content


class DMLogLLMNode(LLMNode):
    """Generates a new DM-Log entry via LLM."""

    def __init__(self, api_key=None, provider="gemini", test_mode=False):
        super().__init__(
            name="dm_log_llm",
            prompt_template=DM_LOG_PROMPT,
            context_keys=["task_name", "today", "task_results", "next_steps", "dm_content"],
            output_key="dm_entry",
            api_key=api_key, provider=provider, test_mode=test_mode
        )

    def prep(self, context):
        return {
            "task_name": context.get("task_name", "Unknown"),
            "today": context.get("today", "N/A"),
            "task_results": "\n".join(f"- {r}" for r in context.get("task_results", [])),
            "next_steps": "\n".join(f"- {s}" for s in context.get("next_steps", [])),
            "current_content": context.get("dm_content", ""),
        }

    def exec(self, context):
        prep_data = self.prep(context)
        prompt = self.prompt_template.format(**prep_data)

        if self.test_mode:
            entry = f"### {context.get('today')} - {context.get('task_name')}\n\n**Tâches accomplies :**\n- Test mode entry\n\n**Prochaines étapes :**\n- Continue"
        else:
            entry = self.llm.generate_text(prompt, model_id=self.model_id)

        context["dm_entry"] = entry
        return entry


class DMLogUpdateNode(BaseNode):
    """Writes the new DM-Log entry into the file."""

    def __init__(self, path="docs/dm-log.md"):
        super().__init__("dm_log_update")
        self.path = path

    def exec(self, context):
        content = context.get("dm_content", "")
        entry = context.get("dm_entry", "")

        marker = "## Résultats des étapes"
        pos = content.find(marker)
        if pos >= 0:
            insert = pos + len(marker)
            updated = content[:insert] + "\n\n" + entry + content[insert:]
        else:
            updated = content + "\n\n" + entry

        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(updated)

        context.setdefault("modified_files", []).append(self.path)
        return True


class DocUpdateNode(LLMNode):
    """Generic document update node - reads file, calls LLM, writes updated version."""

    def __init__(self, name, path, prompt_template, api_key=None, provider="gemini", test_mode=False):
        super().__init__(
            name=name,
            prompt_template=prompt_template,
            output_key=f"{name}_result",
            api_key=api_key, provider=provider, test_mode=test_mode
        )
        self.path = path

    def exec(self, context):
        # Read existing content
        if os.path.exists(self.path):
            with open(self.path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = f"# {self.name.replace('_', ' ').title()}\n\nDocument à initialiser.\n"

        # Call LLM
        prompt = self.prompt_template.format(content=content)

        if self.test_mode:
            updated = f"[TEST] Updated {self.name} - {len(content)} chars processed"
        else:
            updated = self.llm.generate_text(prompt, model_id=self.model_id)

        # Write back
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(updated)

        context.setdefault("modified_files", []).append(self.path)
        return True


class ModelConceptUpdateNode(DocUpdateNode):
    """Updates the MCD & Garde-fous doc."""
    def __init__(self, path="docs/mcd-guardrails.md", **kwargs):
        super().__init__("model_concept_update", path, MCD_PROMPT, **kwargs)


class ProjectStructureUpdateNode(DocUpdateNode):
    """Updates the project structure doc."""
    def __init__(self, path="docs/project-structure.md", **kwargs):
        super().__init__("project_structure_update", path, PROJECT_STRUCTURE_PROMPT, **kwargs)


class TasksUpdateNode(DocUpdateNode):
    """Updates the tasks doc."""
    def __init__(self, path="docs/tasks.md", **kwargs):
        super().__init__("tasks_update", path, TASKS_PROMPT, **kwargs)


class RequirementsUpdateNode(DocUpdateNode):
    """Updates the requirements doc."""
    def __init__(self, path="docs/requirements.md", **kwargs):
        super().__init__("requirements_update", path, REQUIREMENTS_PROMPT, **kwargs)
