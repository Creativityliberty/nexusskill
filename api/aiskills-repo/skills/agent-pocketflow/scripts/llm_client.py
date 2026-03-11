"""
LLM Client — Multi-provider LLM client.

Supports Gemini, OpenAI, and DeepSeek APIs.
Auto-detects API key from environment variables.

Usage:
    llm = LLMClient(provider="gemini")
    response = llm.generate_text("Hello, analyze this...")
"""

import os
import json

try:
    import httpx
except ImportError:
    httpx = None


class LLMClient:
    """Multi-provider LLM client supporting Gemini, OpenAI, and DeepSeek."""

    PROVIDERS = {
        "gemini": {
            "env_keys": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
            "default_model": "gemini-2.5-flash",
        },
        "openai": {
            "env_keys": ["OPENAI_API_KEY"],
            "default_model": "gpt-4o",
        },
        "deepseek": {
            "env_keys": ["DEEPSEEK_API_KEY"],
            "default_model": "deepseek-reasoner",
        },
    }

    def __init__(self, api_key=None, provider="gemini", test_mode=False):
        self.provider = provider.lower()
        self.test_mode = test_mode

        if not test_mode:
            self.api_key = api_key or self._get_api_key()
            if not self.api_key:
                env_keys = self.PROVIDERS.get(self.provider, {}).get("env_keys", [])
                raise ValueError(
                    f"API key for {self.provider} not found. "
                    f"Set one of: {', '.join(env_keys)}"
                )
        else:
            self.api_key = "test-key"

    def _get_api_key(self):
        """Auto-detect API key from environment."""
        config = self.PROVIDERS.get(self.provider, {})
        for key in config.get("env_keys", []):
            val = os.getenv(key)
            if val:
                return val
        return None

    def generate_text(self, prompt, model_id=None, temperature=0.2):
        """Generate text from a prompt."""
        if self.test_mode:
            return f"[TEST] Response for prompt ({len(prompt)} chars)"

        if not httpx:
            raise ImportError("Install httpx: pip install httpx")

        model = model_id or self.PROVIDERS[self.provider]["default_model"]

        if self.provider == "gemini":
            return self._call_gemini(prompt, model, temperature)
        elif self.provider in ("openai", "deepseek"):
            url = {
                "openai": "https://api.openai.com/v1/chat/completions",
                "deepseek": "https://api.deepseek.com/v1/chat/completions",
            }[self.provider]
            return self._call_openai_compat(prompt, model, temperature, url)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _call_gemini(self, prompt, model, temperature):
        """Call Gemini API."""
        url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature},
        }

        response = httpx.post(url, headers=headers, json=payload, timeout=60.0)
        response.raise_for_status()
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]

    def _call_openai_compat(self, prompt, model, temperature, url):
        """Call OpenAI-compatible API (OpenAI or DeepSeek)."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }

        response = httpx.post(url, headers=headers, json=payload, timeout=60.0)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
