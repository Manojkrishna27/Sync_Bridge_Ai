import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from .base_provider import BaseAIProvider
from .mock_provider import MockAIProvider

class GeminiProvider(BaseAIProvider):
    """Google Gemini API Provider with graceful Mock fallback."""

    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.mock_fallback = MockAIProvider()

    def _call_gemini(self, prompt_text: str, temperature: float = 0.4, response_json: bool = False) -> str:
        """Low-level helper: call Gemini generateContent and return the text."""
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        gen_config = {"temperature": temperature}
        if response_json:
            gen_config["responseMimeType"] = "application/json"

        payload = {
            "contents": [{"parts": [{"text": prompt_text}]}],
            "generationConfig": gen_config
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["candidates"][0]["content"]["parts"][0]["text"]

    def chat(
        self,
        system_prompt: str,
        user_message: str,
        context: Optional[str] = None
    ) -> str:
        if not self.api_key:
            return self.mock_fallback.chat(system_prompt, user_message, context)
        try:
            # Gemini doesn't have separate system-role messages in the basic REST API,
            # so we prepend them as a single combined prompt.
            full_prompt = system_prompt
            if context:
                full_prompt += f"\n\nRelevant context from knowledge base:\n{context}"
            full_prompt += f"\n\nUser: {user_message}\n\nAssistant:"
            return self._call_gemini(full_prompt, temperature=0.4).strip()
        except Exception as e:
            return f"[Gemini Error: {str(e)}]\n\n" + self.mock_fallback.chat(system_prompt, user_message, context)

    def generate_mapping_suggestions(
        self,
        source_fields: List[Dict[str, Any]],
        target_fields: List[Dict[str, Any]],
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            return self.mock_fallback.generate_mapping_suggestions(source_fields, target_fields, context)

        try:
            prompt = f"""You are an enterprise integration mapping assistant. Compare source fields and target fields below and suggest semantic field mappings.
Source fields: {json.dumps(source_fields[:30])}
Target fields: {json.dumps(target_fields[:30])}

Return ONLY valid JSON format array of objects with keys:
- source_field (string)
- target_field (string)
- confidence_score (float 0.0 to 1.0)
- reason (string explanation)
- suggested_transformation (string or null)
- suggested_validation (object or null)
"""
            text = self._call_gemini(prompt, temperature=0.2, response_json=True)
            return json.loads(text)
        except Exception:
            return self.mock_fallback.generate_mapping_suggestions(source_fields, target_fields, context)



