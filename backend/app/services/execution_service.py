from typing import Dict, Any, Tuple, Optional, List
from app.repositories.execution_repository import ExecutionRepository
from app.repositories.integration_repository import IntegrationRepository
from app.integration_engine.execution_manager import ExecutionManager
from app.integration_engine.schema_validator import SchemaValidator
from app.integration_engine.payload_parser import PayloadParser
from app.integration_engine.protocol_detector import ProtocolDetector
from app.services.integration_service import IntegrationService

class ExecutionService:
    def __init__(self):
        self.execution_repo = ExecutionRepository()
        self.integration_repo = IntegrationRepository()
        self.integration_service = IntegrationService()
        self.execution_manager = ExecutionManager(self.execution_repo)

    def execute(self, integration_id: str, raw_payload: Any, headers: Dict[str, Any] = None):
        integration = self.integration_service.get_integration(integration_id)
        return self.execution_manager.run_pipeline(integration, raw_payload, headers, mode="EXECUTE")

    def preview(self, integration_id: str, raw_payload: Any, headers: Dict[str, Any] = None):
        integration = self.integration_service.get_integration(integration_id)
        return self.execution_manager.run_pipeline(integration, raw_payload, headers, mode="PREVIEW")

    def validate_payload(self, integration_id: str, raw_payload: Any, headers: Dict[str, Any] = None) -> Dict[str, Any]:
        integration = self.integration_service.get_integration(integration_id)
        detected_protocol = ProtocolDetector.detect(raw_payload, headers)
        parsed_payload = PayloadParser.parse(raw_payload, detected_protocol, integration.config or {})
        schema = (integration.config or {}).get("schema", {})
        is_valid, errors = SchemaValidator.validate(parsed_payload, schema)
        return {
            "valid": is_valid,
            "detected_protocol": detected_protocol,
            "errors": errors,
            "parsed_payload": parsed_payload
        }

    def get_history(
        self,
        integration_id: str,
        page: int = 1,
        per_page: int = 10,
        status: Optional[str] = None
    ) -> Tuple[List, int]:
        return self.execution_repo.get_by_integration(integration_id, page=page, per_page=per_page, status=status)

    def get_execution(self, execution_id: str):
        execution = self.execution_repo.get_execution_detail(execution_id)
        if not execution:
            raise ValueError("Execution record not found")
        return execution
