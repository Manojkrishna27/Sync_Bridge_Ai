from typing import Any, Dict
from .base_connector import BaseConnector

class SFTPConnector(BaseConnector):
    """Connector implementation for SFTP file transfer and polling."""

    def validate(self, config: Dict[str, Any]) -> bool:
        return bool(config and "host" in config and "port" in config)

    def parse(self, payload: Any) -> Dict[str, Any]:
        return {"file_content": payload}

    def transform(self, data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        return data

    def send(self, data: Dict[str, Any], endpoint_config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "protocol": "SFTP", "remote_path": endpoint_config.get("path")}

    def receive(self, source_config: Dict[str, Any]) -> Any:
        return b""
