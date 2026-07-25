import os
import json
from typing import Dict, Any, List
from .base_provider import BaseAIProvider
from .mock_provider import MockAIProvider

class OpenAIProvider(BaseAIProvider):
    """OpenAI API Provider with graceful Mock fallback."""

    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.mock_fallback = MockAIProvider()

    def generate_mapping_suggestions(
        self,
        source_fields: List[Dict[str, Any]],
        target_fields: List[Dict[str, Any]],
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            # Fallback to heuristic provider when no API key configured
            return self.mock_fallback.generate_mapping_suggestions(source_fields, target_fields, context)

        try:
            import openai
            openai.api_key = self.api_key

            prompt = f"""You are an enterprise integration mapping assistant. Compare source fields and target fields below and suggest semantic field mappings.
Source fields: {json.dumps(source_fields[:30])}
Target fields: {json.dumps(target_fields[:30])}

Return a JSON array of objects with keys:
- source_field (string)
- target_field (string)
- confidence_score (float 0.0 to 1.0)
- reason (string explanation)
- suggested_transformation (string or null)
- suggested_validation (object or null)
"""

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )

            content = response.choices[0].message.content
            return json.loads(content)
        except Exception:
            return self.mock_fallback.generate_mapping_suggestions(source_fields, target_fields, context)
