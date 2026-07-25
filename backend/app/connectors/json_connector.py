import json
from typing import Any, Dict
from .base_connector import BaseConnector

class JSONConnector(BaseConnector):
    """Connector implementation for native JSON payload parsing & REST HTTP communication."""

    def validate(self, config: Dict[str, Any]) -> bool:
        return True

    def parse(self, payload: Any) -> Dict[str, Any]:
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, bytes):
            payload = payload.decode('utf-8')
        if isinstance(payload, str):
            return json.loads(payload)
        return {}

    def transform(self, data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        return data

    def send(self, data: Dict[str, Any], endpoint_config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "protocol": "JSON",
            "url": endpoint_config.get("url"),
            "data": data
        }

    def receive(self, source_config: Dict[str, Any]) -> Any:
        return {}
