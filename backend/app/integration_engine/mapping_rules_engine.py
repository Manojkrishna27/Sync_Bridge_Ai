import re
from datetime import datetime
from typing import Dict, Any, List

class MappingRulesEngine:
    """
    Dedicated Mapping Rules Engine.
    Executes static, nested, conditional, lookup, array mappings, default values,
    and custom transformation functions.
    """

    TRANSFORM_FUNCTIONS = {
        "capitalize": lambda v: str(v).capitalize() if v is not None else None,
        "uppercase": lambda v: str(v).upper() if v is not None else None,
        "lowercase": lambda v: str(v).lower() if v is not None else None,
        "number_int": lambda v: int(v) if v is not None and str(v).isdigit() else 0,
        "boolean_cast": lambda v: bool(v) if v is not None else False,
        "date_iso": lambda v: datetime.utcnow().isoformat() if v == "now" or not v else str(v),
        "currency_usd": lambda v: f"${float(v):,.2f}" if v is not None else "$0.00"
    }

    @classmethod
    def apply_rules(cls, source_data: Dict[str, Any], rules_config: Dict[str, Any]) -> Dict[str, Any]:
        result = {}

        if not rules_config:
            return dict(source_data)

        # 1. Direct / Static Field Mappings
        mappings = rules_config.get("mappings", {})
        for src_path, target_path in mappings.items():
            val = cls._get_nested_val(source_data, src_path)
            if val is not None:
                cls._set_nested_val(result, target_path, val)

        # 2. Default Values
        defaults = rules_config.get("defaults", {})
        for target_path, default_val in defaults.items():
            if cls._get_nested_val(result, target_path) is None:
                cls._set_nested_val(result, target_path, default_val)

        # 3. Lookup Table Mappings (Check source_data or result)
        lookups = rules_config.get("lookups", {})
        for field_path, lookup_table in lookups.items():
            current_val = cls._get_nested_val(result, field_path)
            if current_val is None:
                current_val = cls._get_nested_val(source_data, field_path)

            if current_val in lookup_table:
                cls._set_nested_val(result, field_path, lookup_table[current_val])

        # 4. Conditional Mappings
        conditionals = rules_config.get("conditionals", [])
        for cond in conditionals:
            cls._apply_conditional_rule(source_data, result, cond)

        # 5. Transformations (Functions)
        transforms = rules_config.get("transformations", {})
        for target_path, func_name in transforms.items():
            current_val = cls._get_nested_val(result, target_path)
            if func_name in cls.TRANSFORM_FUNCTIONS:
                func = cls.TRANSFORM_FUNCTIONS[func_name]
                transformed_val = func(current_val)
                cls._set_nested_val(result, target_path, transformed_val)

        # 6. Array Mappings
        array_mappings = rules_config.get("array_mappings", [])
        for arr_rule in array_mappings:
            cls._apply_array_mapping(source_data, result, arr_rule)

        return result

    @classmethod
    def _apply_conditional_rule(cls, source_data: dict, result: dict, cond: dict):
        src_field = cond.get("if_field")
        expected_val = cond.get("equals")
        target_field = cond.get("then_field")
        then_val = cond.get("then_value")
        else_val = cond.get("else_value")

        actual_val = cls._get_nested_val(source_data, src_field)
        if actual_val == expected_val:
            cls._set_nested_val(result, target_field, then_val)
        elif else_val is not None:
            cls._set_nested_val(result, target_field, else_val)

    @classmethod
    def _apply_array_mapping(cls, source_data: dict, result: dict, arr_rule: dict):
        src_arr_path = arr_rule.get("source_array")
        target_arr_path = arr_rule.get("target_array")
        item_mappings = arr_rule.get("item_mappings", {})

        source_list = cls._get_nested_val(source_data, src_arr_path)
        if isinstance(source_list, list):
            transformed_list = []
            for item in source_list:
                if isinstance(item, dict):
                    transformed_item = {}
                    for s_k, t_k in item_mappings.items():
                        val = item.get(s_k)
                        if val is not None:
                            transformed_item[t_k] = val
                    transformed_list.append(transformed_item)
                else:
                    transformed_list.append(item)
            cls._set_nested_val(result, target_arr_path, transformed_list)

    @classmethod
    def _get_nested_val(cls, data: dict, path: str) -> Any:
        if not isinstance(data, dict) or not path:
            return None
        parts = path.split(".")
        curr = data
        for p in parts:
            if isinstance(curr, dict) and p in curr:
                curr = curr[p]
            else:
                return None
        return curr

    @classmethod
    def _set_nested_val(cls, data: dict, path: str, value: Any):
        parts = path.split(".")
        curr = data
        for i, p in enumerate(parts[:-1]):
            if p not in curr or not isinstance(curr[p], dict):
                curr[p] = {}
            curr = curr[p]
        curr[parts[-1]] = value
