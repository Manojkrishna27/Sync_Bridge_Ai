from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseAIService(ABC):
    """
    Abstract Base Class for pluggable AI modules in the Gateway.
    Allows schema mapping, error analysis, payload analysis, and copilot actions
    to be injected seamlessly without modifying core business services.
    """

    @abstractmethod
    def map_schema(self, source_schema: Dict[str, Any], target_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate automated field mapping recommendations between source & target schemas."""
        pass

    @abstractmethod
    def explain_error(self, error_message: str, stack_trace: Optional[str] = None) -> Dict[str, Any]:
        """Provide human-readable diagnostics and resolution suggestions for integration failures."""
        pass

    @abstractmethod
    def analyze_payload(self, payload: Any) -> Dict[str, Any]:
        """Inspect integration payload structure and detect anomalies or validation issues."""
        pass

    @abstractmethod
    def assist_documentation(self, integration_config: Dict[str, Any]) -> str:
        """Generate automated technical documentation for an integration definition."""
        pass

    @abstractmethod
    def copilot_assist(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide AI copilot assistance for building and troubleshooting integrations."""
        pass

class DefaultAIService(BaseAIService):
    """Default non-blocking stub implementation for AI services."""

    def map_schema(self, source_schema: Dict[str, Any], target_schema: Dict[str, Any]) -> Dict[str, Any]:
        return {"mappings": {}, "confidence": 1.0, "status": "stub"}

    def explain_error(self, error_message: str, stack_trace: Optional[str] = None) -> Dict[str, Any]:
        return {"explanation": error_message, "recommendation": "Check endpoint connection and payload validation.", "status": "stub"}

    def analyze_payload(self, payload: Any) -> Dict[str, Any]:
        return {"insights": ["Valid payload format"], "status": "stub"}

    def assist_documentation(self, integration_config: Dict[str, Any]) -> str:
        return f"Integration documentation for {integration_config.get('name', 'Integration')}."

    def copilot_assist(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"response": f"AI Copilot processed request: {prompt}", "status": "stub"}
