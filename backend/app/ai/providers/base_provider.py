from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAIProvider(ABC):
    """Abstract Base Class for AI Mapping Providers."""

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
