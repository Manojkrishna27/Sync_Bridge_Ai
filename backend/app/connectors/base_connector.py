from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseConnector(ABC):
    """
    Abstract Base Class for all Integration Gateway Connectors.
    Exposes common pluggable interface for future execution engine operations.
    """

    @abstractmethod
    def validate(self, config: Dict[str, Any]) -> bool:
        """Validate connection configurations and payload parameters."""
        pass

    @abstractmethod
    def parse(self, payload: Any) -> Dict[str, Any]:
        """Parse raw incoming protocol payload into standard Python dictionary."""
        pass

    @abstractmethod
    def transform(self, data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Apply transformation and mapping rules to standardized data."""
        pass

    @abstractmethod
    def send(self, data: Dict[str, Any], endpoint_config: Dict[str, Any]) -> Dict[str, Any]:
        """Send formatted data to destination system."""
        pass

    @abstractmethod
    def receive(self, source_config: Dict[str, Any]) -> Any:
        """Fetch or receive raw data payload from source system."""
        pass
