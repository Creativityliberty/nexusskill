"""
LLM Node — Node that calls an LLM with a prompt template.

Combines PocketFlow's Node pattern with a multi-provider LLM client.
Supports Gemini, OpenAI, and DeepSeek out of the box.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nodes.base_node import BaseNode
from llm_client import LLMClient


class LLMNode(BaseNode):
    """
    A node that sends a prompt to an LLM and stores the response.
    
    Usage:
        node = LLMNode(
            name="analyze",
            prompt_template="Analyze this code:\n{code}",
            context_keys=["code"],
            output_key="analysis"
        )
    """

    def __init__(self, name: str, prompt_template: str = "",
                 context_keys: list = None, output_key: str = None,
                 api_key: str = None, provider: str = "gemini",
                 model_id: str = None, test_mode: bool = False):
        super().__init__(name)
        self.prompt_template = prompt_template
        self.context_keys = context_keys or []
        self.output_key = output_key or f"{name}_result"
        self.test_mode = test_mode

        if not test_mode:
            self.llm = LLMClient(api_key=api_key, provider=provider, test_mode=test_mode)
        else:
            self.llm = None
        self.model_id = model_id

    def prep(self, context: dict) -> dict:
        """Extract the needed values from context for the prompt."""
        return {key: context.get(key, "") for key in self.context_keys}

    def exec(self, context: dict) -> any:
        """Format the prompt and call the LLM."""
        # Gather template variables
        prep_data = self.prep(context)

        # Format the prompt
        try:
            prompt = self.prompt_template.format(**prep_data)
        except KeyError as e:
            prompt = self.prompt_template  # fallback if missing keys

        # Call LLM (or return test response)
        if self.test_mode:
            response = f"[TEST MODE] Response for {self.name}: Prompt received ({len(prompt)} chars)"
        else:
            response = self.llm.generate_text(prompt, model_id=self.model_id)

        # Store in context
        context[self.output_key] = response
        return response

    def post(self, context: dict, exec_result: any) -> str:
        """Store the LLM response."""
        context[f"result_{self.name}"] = exec_result
        return "default"
