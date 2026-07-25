import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List
from .base_provider import BaseAIProvider
from .mock_provider import MockAIProvider

class GeminiProvider(BaseAIProvider):
    """Google Gemini API Provider with graceful Mock fallback."""

    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.mock_fallback = MockAIProvider()

    def generate_mapping_suggestions(
        self,
        source_fields: List[Dict[str, Any]],
        target_fields: List[Dict[str, Any]],
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            return self.mock_fallback.generate_mapping_suggestions(source_fields, target_fields, context)

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
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

            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json"
                }
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                text_content = result['candidates'][0]['content']['parts'][0]['text']
                return json.loads(text_content)
        except Exception:
            return self.mock_fallback.generate_mapping_suggestions(source_fields, target_fields, context)
