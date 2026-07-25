from typing import Dict, Any, Optional
from flask import jsonify, make_response

class EnterpriseErrorCategory:
    PARSE_ERROR = "PARSE_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    TRANSFORMATION_ERROR = "TRANSFORMATION_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    SECURITY_ERROR = "SECURITY_ERROR"
    SYSTEM_ERROR = "SYSTEM_ERROR"

class ResponseBuilder:
    """Response Builder & Standardized Enterprise Error Model."""

    @staticmethod
    def build_success_response(
        data: Any,
        correlation_id: str,
        status_code: int = 200,
        meta: Optional[Dict[str, Any]] = None
    ):
        response_payload = {
            "success": True,
            "correlation_id": correlation_id,
            "data": data
        }
        if meta:
            response_payload["meta"] = meta

        response = make_response(jsonify(response_payload), status_code)
        response.headers["X-Correlation-ID"] = correlation_id
        return response

    @staticmethod
    def build_error_response(
        error_code: str,
        category: str,
        message: str,
        correlation_id: str,
        status_code: int = 400,
        technical_details: Optional[str] = None,
        suggested_resolution: Optional[str] = None
    ):
        error_payload = {
            "success": False,
            "error_code": error_code,
            "category": category,
            "message": message,
            "technical_details": technical_details or "Refer to correlation ID in server logs",
            "correlation_id": correlation_id,
            "suggested_resolution": suggested_resolution or "Check payload format and validation rules"
        }

        response = make_response(jsonify(error_payload), status_code)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
