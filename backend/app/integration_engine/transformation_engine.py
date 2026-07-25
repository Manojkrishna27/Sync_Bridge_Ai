from typing import Dict, Any
from .mapping_rules_engine import MappingRulesEngine

class TransformationEngine:
    """
    Transformation Engine middleware consuming the dedicated MappingRulesEngine.
    Refactored to separate transformation execution from mapping definition.
    """

    @staticmethod
    def transform(parsed_payload: Dict[str, Any], mapping_config: Dict[str, Any]) -> Dict[str, Any]:
        if not parsed_payload:
            return {}

        # Delegates to MappingRulesEngine
        transformed = MappingRulesEngine.apply_rules(parsed_payload, mapping_config or {})
        return transformed
