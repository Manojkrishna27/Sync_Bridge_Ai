from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseAIProvider(ABC):
    """Abstract Base Class for AI Providers — mapping suggestions + chat completion."""

    @abstractmethod
    def generate_mapping_suggestions(
        self,
        source_fields: List[Dict[str, Any]],
        target_fields: List[Dict[str, Any]],
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates list of mapping suggestions.
        Each item must contain:
          - source_field (str)
          - target_field (str)
          - confidence_score (float 0.0 - 1.0)
          - reason (str)
          - suggested_transformation (str or None)
          - suggested_validation (dict or None)
        """
        pass

    @abstractmethod
    def chat(
        self,
        system_prompt: str,
        user_message: str,
        context: Optional[str] = None
    ) -> str:
        """
        Send a chat completion request to the LLM.
        Returns the assistant's response text.
        """
        pass

