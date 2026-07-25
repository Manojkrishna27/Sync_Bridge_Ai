import time
import uuid
from datetime import datetime
from typing import Dict, Any, Tuple
from flask import g, request, has_request_context

from app.models.integration_execution import IntegrationExecution, ExecutionLog, ExecutionError
from app.models.monitoring_model import ExecutionMetrics
from app.connectors import get_connector
from app.integration_engine.protocol_detector import ProtocolDetector
from app.integration_engine.payload_parser import PayloadParser
from app.integration_engine.schema_validator import SchemaValidator
from app.integration_engine.transformation_engine import TransformationEngine
from app.integration_engine.response_builder import ResponseBuilder, EnterpriseErrorCategory
from app.core.logger import get_logger
from app.core.extensions import db

logger = get_logger()

class ExecutionManager:
    """
    Enterprise Execution Manager orchestrating Middleware Pipeline, Performance Profiling & OpenTelemetry Trace Propagation.
    """

    def __init__(self, execution_repo=None):
        self.execution_repo = execution_repo

    def run_pipeline(
        self,
        integration,
        raw_payload: Any,
        headers: Dict[str, Any] = None,
        mode: str = "EXECUTE"
    ) -> Tuple[Any, int]:
        
        start_time = time.time()
        headers = headers or {}
        correlation_id = getattr(g, "correlation_id", str(uuid.uuid4()))
        trace_id = headers.get("X-Trace-ID") or getattr(g, "trace_id", str(uuid.uuid4()))

        execution = IntegrationExecution(
            id=str(uuid.uuid4()),
            correlation_id=correlation_id,
            client_id=integration.client_id,
            integration_id=integration.id,
            status="PENDING",
            protocol=integration.source_protocol or "JSON",
            execution_mode=mode,
            payload_size=len(str(raw_payload)) if raw_payload else 0,
            received_at=datetime.utcnow(),
            request_payload=str(raw_payload)[:5000] if raw_payload else None
        )

        logs = []
        errors = []

        # Profiling Timers (ms)
        t_parsing_ms = 0.0
        t_val_ms = 0.0
        t_trans_ms = 0.0
        t_ext_ms = 0.0
        t_db_ms = 0.0

        try:
            # 1. Protocol Detection
            detected_protocol = ProtocolDetector.detect(raw_payload, headers)
            execution.protocol = detected_protocol
            execution.parsed_at = datetime.utcnow()
            logs.append(ExecutionLog(step_name="PROTOCOL_DETECTION", log_level="INFO", message=f"Detected protocol: {detected_protocol}"))

            # 2. Payload Parsing Stage
            t_parse_start = time.time()
            parsed_payload = PayloadParser.parse(raw_payload, detected_protocol, integration.config or {})
            t_parsing_ms = round((time.time() - t_parse_start) * 1000, 2)
            execution.parsing_time_ms = t_parsing_ms
            logs.append(ExecutionLog(step_name="PARSING", log_level="INFO", message="Payload parsed successfully"))

            # 3. Schema Validation Stage
            t_val_start = time.time()
            schema = (integration.config or {}).get("schema", {})
            is_valid, val_errors = SchemaValidator.validate(parsed_payload, schema)
            execution.validated_at = datetime.utcnow()
            t_val_ms = round((time.time() - t_val_start) * 1000, 2)
            execution.validation_time_ms = t_val_ms

            if not is_valid:
                execution.status = "VALIDATION_ERROR"
                for err in val_errors:
                    errors.append(ExecutionError(
                        error_code=err.get("error_code", "ERR_VAL_001"),
                        category=EnterpriseErrorCategory.VALIDATION_ERROR,
                        message=err.get("message"),
                        technical_details=f"Validation rule violated on field: {err.get('field')}",
                        suggested_resolution="Update payload fields to match schema definitions."
                    ))

                if mode == "EXECUTE":
                    self._persist_execution(execution, logs, errors, trace_id, t_parsing_ms, t_val_ms, t_trans_ms, t_ext_ms)

                return ResponseBuilder.build_error_response(
                    error_code="ERR_VAL_001",
                    category=EnterpriseErrorCategory.VALIDATION_ERROR,
                    message="Payload schema validation failed",
                    correlation_id=correlation_id,
                    status_code=400
                )

            # 4. Transformation Stage
            t_trans_start = time.time()
            mapping_config = (integration.config or {}).get("mapping_config", {})
            transformed_payload = TransformationEngine.transform(parsed_payload, mapping_config)
            execution.transformed_at = datetime.utcnow()
            t_trans_ms = round((time.time() - t_trans_start) * 1000, 2)
            execution.transformation_time_ms = t_trans_ms

            # PREVIEW MODE
            if mode == "PREVIEW":
                return ResponseBuilder.build_success_response(
                    data={
                        "preview": True,
                        "protocol": detected_protocol,
                        "parsed_payload": parsed_payload,
                        "transformed_payload": transformed_payload,
                        "profiling_ms": {
                            "parsing_time": t_parsing_ms,
                            "validation_time": t_val_ms,
                            "transformation_time": t_trans_ms
                        }
                    },
                    correlation_id=correlation_id
                )

            # 5. External API / Dispatch Stage
            t_ext_start = time.time()
            execution.sent_at = datetime.utcnow()

            connector = get_connector(integration.destination_protocol or "REST")
            endpoint_config = (integration.config or {}).get("endpoint", {})
            dispatch_result = connector.send(transformed_payload, endpoint_config)

            t_ext_ms = round((time.time() - t_ext_start) * 1000, 2)
            execution.request_time_ms = t_ext_ms
            execution.status = "SUCCESS"
            execution.completed_at = datetime.utcnow()
            execution.total_time_ms = round((time.time() - start_time) * 1000, 2)

            self._persist_execution(execution, logs, errors, trace_id, t_parsing_ms, t_val_ms, t_trans_ms, t_ext_ms)

            response = ResponseBuilder.build_success_response(
                data=dispatch_result,
                correlation_id=correlation_id,
                meta={
                    "total_time_ms": execution.total_time_ms,
                    "version": integration.version
                }
            )
            response.headers["X-Trace-ID"] = trace_id
            return response

        except Exception as ex:
            logger.error(f"Execution failed for integration {integration.id}: {str(ex)}", exc_info=True)
            execution.status = "FAILED"
            execution.dlq_eligible = True
            execution.completed_at = datetime.utcnow()
            execution.total_time_ms = round((time.time() - start_time) * 1000, 2)

            errors.append(ExecutionError(
                error_code="ERR_SYS_001",
                category=EnterpriseErrorCategory.SYSTEM_ERROR,
                message=str(ex),
                technical_details="Unhandled execution pipeline error",
                suggested_resolution="Check connector endpoint reachability and server logs."
            ))

            if mode == "EXECUTE":
                self._persist_execution(execution, logs, errors, trace_id, t_parsing_ms, t_val_ms, t_trans_ms, t_ext_ms)

            response = ResponseBuilder.build_error_response(
                error_code="ERR_SYS_001",
                category=EnterpriseErrorCategory.SYSTEM_ERROR,
                message=str(ex),
                correlation_id=correlation_id,
                status_code=500
            )
            response.headers["X-Trace-ID"] = trace_id
            return response

    def _persist_execution(self, execution, logs, errors, trace_id, t_parsing, t_val, t_trans, t_ext):
        try:
            t_db_start = time.time()
            db.session.add(execution)
            for l in logs:
                l.execution_id = execution.id
                db.session.add(l)
            for e in errors:
                e.execution_id = execution.id
                db.session.add(e)

            # Record Detailed Performance Metrics Snapshot
            metrics = ExecutionMetrics(
                id=str(uuid.uuid4()),
                correlation_id=execution.correlation_id,
                trace_id=trace_id,
                client_id=execution.client_id,
                integration_id=execution.integration_id,
                db_time_ms=round((time.time() - t_db_start) * 1000, 2),
                cache_time_ms=0.5,
                parsing_time_ms=t_parsing,
                validation_time_ms=t_val,
                ai_time_ms=0.0,
                transformation_time_ms=t_trans,
                external_api_time_ms=t_ext,
                total_time_ms=execution.total_time_ms
            )
            db.session.add(metrics)
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to persist execution history and metrics: {str(e)}")
            db.session.rollback()
