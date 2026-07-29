import os
import json
from typing import Dict, Any, List, Optional
from .base_provider import BaseAIProvider
from .mock_provider import MockAIProvider


class OpenRouterProvider(BaseAIProvider):
    """
    OpenRouter Provider — OpenAI-compatible API gateway supporting 200+ models.
    Uses https://openrouter.ai/api/v1 as the base URL.
    Default model: mistralai/mistral-7b-instruct:free (no cost)
    """

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct:free")
        self.mock_fallback = MockAIProvider()

    def _get_client(self):
        import openai
        return openai.OpenAI(
            api_key=self.api_key,
            base_url=self.BASE_URL,
            default_headers={
                "HTTP-Referer": "https://syncbridge.ai",   # shown in OpenRouter dashboard
                "X-Title": "SyncBridge AI Copilot"
            }
        )

    def chat(
        self,
        system_prompt: str,
        user_message: str,
        context: Optional[str] = None
    ) -> str:
        if not self.api_key:
            return self.mock_fallback.chat(system_prompt, user_message, context)
        try:
            client = self._get_client()
            messages = [{"role": "system", "content": system_prompt}]
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Relevant context from knowledge base:\n{context}"
                })
            messages.append({"role": "user", "content": user_message})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.4,
                max_tokens=1024
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return (
                f"[OpenRouter Error: {str(e)}]\n\n"
                + self.mock_fallback.chat(system_prompt, user_message, context)
            )

    def generate_mapping_suggestions(
        self,
        source_fields: List[Dict[str, Any]],
        target_fields: List[Dict[str, Any]],
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            return self.mock_fallback.generate_mapping_suggestions(source_fields, target_fields, context)

        try:
            client = self._get_client()
            prompt = f"""You are an enterprise integration mapping assistant. Compare source fields and target fields below and suggest semantic field mappings.
Source fields: {json.dumps(source_fields[:30])}
Target fields: {json.dumps(target_fields[:30])}

Return ONLY a valid JSON array of objects with keys:
- source_field (string)
- target_field (string)
- confidence_score (float 0.0 to 1.0)
- reason (string explanation)
- suggested_transformation (string or null)
- suggested_validation (object or null)
"""
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=2048
            )
            content = response.choices[0].message.content.strip()
            # Strip markdown code fences if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except Exception:
            return self.mock_fallback.generate_mapping_suggestions(source_fields, target_fields, context)
