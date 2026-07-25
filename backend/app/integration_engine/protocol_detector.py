import re
import json
from typing import Any

class ProtocolDetector:
    """Automatic protocol and payload format detection engine."""

    @staticmethod
    def detect(payload: Any, headers: dict = None) -> str:
        headers = headers or {}
        
        # Check HTTP Headers first
        content_type = headers.get("Content-Type", "").lower()
        soap_action = headers.get("SOAPAction") or headers.get("soapaction")
        
        if soap_action or "soap+xml" in content_type:
            return "SOAP"

        if not payload:
            return "JSON"

        # Convert bytes to string for pattern inspection
        if isinstance(payload, bytes):
            try:
                payload_str = payload.decode('utf-8').strip()
            except Exception:
                return "BINARY"
        elif isinstance(payload, str):
            payload_str = payload.strip()
        elif isinstance(payload, (dict, list)):
            return "JSON"
        else:
            payload_str = str(payload).strip()

        # SOAP Inspection
        if "<soap:Envelope" in payload_str or "<soapenv:Envelope" in payload_str or "<Envelope" in payload_str:
            if "schemas.xmlsoap.org" in payload_str or "www.w3.org/2003/05/soap-envelope" in payload_str:
                return "SOAP"

        # XML Inspection
        if payload_str.startswith("<?xml") or (payload_str.startswith("<") and payload_str.endswith(">")):
            return "XML"

        # JSON Inspection
        if (payload_str.startswith("{") and payload_str.endswith("}")) or (payload_str.startswith("[") and payload_str.endswith("]")):
            try:
                json.loads(payload_str)
                return "JSON"
            except Exception:
                pass

        # CSV Inspection (Comma / Semicolon / Tab separated lines)
        lines = [line.strip() for line in payload_str.splitlines() if line.strip()]
        if len(lines) >= 1:
            first_line = lines[0]
            if "," in first_line or ";" in first_line or "\t" in first_line:
                delimiter = "," if "," in first_line else (";" if ";" in first_line else "\t")
                cols = first_line.split(delimiter)
                if len(cols) > 1:
                    return "CSV"

        return "JSON"
