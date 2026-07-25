from typing import Dict, Type
from .base_connector import BaseConnector
from .rest_connector import RESTConnector
from .soap_connector import SOAPConnector
from .xml_connector import XMLConnector
from .csv_connector import CSVConnector
from .json_connector import JSONConnector
from .graphql_connector import GraphQLConnector
from .grpc_connector import gRPCConnector
from .sftp_connector import SFTPConnector

class ConnectorRegistry:
    """
    Auto-discovering Connector Registry.
    Registers protocol connectors dynamically without requiring modifications to the core engine.
    """
    _registry: Dict[str, Type[BaseConnector]] = {}

    @classmethod
    def register(cls, protocol_name: str, connector_cls: Type[BaseConnector]):
        cls._registry[protocol_name.upper()] = connector_cls

    @classmethod
    def get(cls, protocol_name: str) -> BaseConnector:
        normalized = protocol_name.upper()
        connector_cls = cls._registry.get(normalized, RESTConnector)
        return connector_cls()

    @classmethod
    def list_supported_protocols(cls) -> list:
        return list(cls._registry.keys())

# Auto-register core connectors upon module import
ConnectorRegistry.register("REST", RESTConnector)
ConnectorRegistry.register("SOAP", SOAPConnector)
ConnectorRegistry.register("XML", XMLConnector)
ConnectorRegistry.register("CSV", CSVConnector)
ConnectorRegistry.register("JSON", JSONConnector)
ConnectorRegistry.register("GRAPHQL", GraphQLConnector)
ConnectorRegistry.register("GRPC", gRPCConnector)
ConnectorRegistry.register("SFTP", SFTPConnector)

get_connector = ConnectorRegistry.get

__all__ = [
    "ConnectorRegistry",
    "BaseConnector",
    "RESTConnector",
    "SOAPConnector",
    "XMLConnector",
    "CSVConnector",
    "JSONConnector",
    "GraphQLConnector",
    "gRPCConnector",
    "SFTPConnector",
    "get_connector",
]
