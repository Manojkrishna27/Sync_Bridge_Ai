import re
import uuid
from datetime import datetime
from typing import Dict, Any, List, Tuple

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?[1-9]\d{1,14}$")

class SchemaValidator:
    """Enterprise Schema & Payload Validation Engine."""

    @staticmethod
    def validate(payload: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        errors = []

        if not schema:
            return True, []

        required_fields = schema.get("required", [])
        field_types = schema.get("properties", {})
        allow_unknown = schema.get("allow_unknown_fields", True)

        # Check Required Fields
        for req in required_fields:
            if SchemaValidator._get_nested_val(payload, req) is None:
                errors.append({
                    "field": req,
                    "error_code": "ERR_VAL_MISSING",
                    "message": f"Required field '{req}' is missing"
                })

        # Validate Properties
        for field_name, rules in field_types.items():
            val = SchemaValidator._get_nested_val(payload, field_name)
            if val is not None:
                field_errors = SchemaValidator._validate_field_rules(field_name, val, rules)
                errors.extend(field_errors)

        # Unknown Fields check
        if not allow_unknown:
            defined_keys = set(field_types.keys())
            payload_keys = set(payload.keys())
            unknown = payload_keys - defined_keys
            for unk in unknown:
                errors.append({
                    "field": unk,
                    "error_code": "ERR_VAL_UNKNOWN_FIELD",
                    "message": f"Unknown field '{unk}' is not allowed by schema"
                })

        return len(errors) == 0, errors

    @staticmethod
    def _validate_field_rules(field: str, val: Any, rules: Dict[str, Any]) -> List[Dict[str, Any]]:
        errors = []
        expected_type = rules.get("type")

        # Type Checks
        if expected_type:
            if expected_type == "string" and not isinstance(val, str):
                errors.append({"field": field, "error_code": "ERR_VAL_TYPE", "message": f"Expected string for '{field}'"})
            elif expected_type == "integer" and not isinstance(val, int):
                errors.append({"field": field, "error_code": "ERR_VAL_TYPE", "message": f"Expected integer for '{field}'"})
            elif expected_type == "float" and not isinstance(val, (float, int)):
                errors.append({"field": field, "error_code": "ERR_VAL_TYPE", "message": f"Expected float for '{field}'"})
            elif expected_type == "boolean" and not isinstance(val, bool):
                errors.append({"field": field, "error_code": "ERR_VAL_TYPE", "message": f"Expected boolean for '{field}'"})
            elif expected_type == "array" and not isinstance(val, list):
                errors.append({"field": field, "error_code": "ERR_VAL_TYPE", "message": f"Expected array for '{field}'"})
            elif expected_type == "object" and not isinstance(val, dict):
                errors.append({"field": field, "error_code": "ERR_VAL_TYPE", "message": f"Expected object for '{field}'"})

        # Format Checks
        fmt = rules.get("format")
        if fmt and isinstance(val, str):
            if fmt == "email" and not EMAIL_REGEX.match(val):
                errors.append({"field": field, "error_code": "ERR_VAL_FORMAT", "message": f"Invalid email format in '{field}'"})
            elif fmt == "phone" and not PHONE_REGEX.match(val):
                errors.append({"field": field, "error_code": "ERR_VAL_FORMAT", "message": f"Invalid phone number format in '{field}'"})
            elif fmt == "uuid":
                try:
                    uuid.UUID(val)
                except ValueError:
                    errors.append({"field": field, "error_code": "ERR_VAL_FORMAT", "message": f"Invalid UUID format in '{field}'"})
            elif fmt == "date":
                try:
                    datetime.fromisoformat(val.replace("Z", "+00:00"))
                except ValueError:
                    errors.append({"field": field, "error_code": "ERR_VAL_FORMAT", "message": f"Invalid ISO date format in '{field}'"})

        # Enum Checks
        allowed_enum = rules.get("enum")
        if allowed_enum and val not in allowed_enum:
            errors.append({
                "field": field,
                "error_code": "ERR_VAL_ENUM",
                "message": f"Value '{val}' for '{field}' is not in allowed enums: {allowed_enum}"
            })

        return errors

    @staticmethod
    def _get_nested_val(data: dict, key_path: str) -> Any:
        if not isinstance(data, dict):
            return None
        parts = key_path.split(".")
        curr = data
        for p in parts:
            if isinstance(curr, dict) and p in curr:
                curr = curr[p]
            else:
                return None
        return curr
