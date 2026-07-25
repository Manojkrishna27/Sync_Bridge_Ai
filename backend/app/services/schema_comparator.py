from typing import Dict, Any, List
from .schema_analyzer import SchemaAnalyzer

class SchemaComparator:
    """
    Schema Comparison & Compatibility Analysis Engine.
    Computes structural diffs, missing/extra fields, type changes, breaking changes, and compatibility scores.
    """

    @staticmethod
    def compare(schema_a_tree: dict, schema_b_tree: dict) -> dict:
        fields_a = {f['path']: f for f in SchemaAnalyzer.extract_flat_fields(schema_a_tree)}
        fields_b = {f['path']: f for f in SchemaAnalyzer.extract_flat_fields(schema_b_tree)}

        paths_a = set(fields_a.keys())
        paths_b = set(fields_b.keys())

        missing_in_b = list(paths_a - paths_b)
        extra_in_b = list(paths_b - paths_a)
        common_paths = paths_a.intersection(paths_b)

        type_changes = []
        breaking_changes = []

        # Analyze missing required fields (Breaking Change)
        for missing_p in missing_in_b:
            field_info = fields_a[missing_p]
            if field_info.get("required", False):
                breaking_changes.append({
                    "path": missing_p,
                    "reason": "Required field was removed in new schema"
                })

        # Analyze common paths for data type mutations
        for common_p in common_paths:
            type_a = fields_a[common_p].get("type")
            type_b = fields_b[common_p].get("type")
            if type_a != type_b:
                change = {
                    "path": common_p,
                    "old_type": type_a,
                    "new_type": type_b
                }
                type_changes.append(change)
                # Type changes on existing fields are treated as breaking
                breaking_changes.append({
                    "path": common_p,
                    "reason": f"Type mutated from {type_a} to {type_b}"
                })

        # Calculate Compatibility Score (0 to 100%)
        total_fields = max(len(paths_a), 1)
        issues_count = len(missing_in_b) + len(type_changes)
        compatibility_score = max(0.0, round(((total_fields - issues_count) / total_fields) * 100, 2))

        return {
            "compatibility_score": compatibility_score,
            "is_compatible": len(breaking_changes) == 0,
            "missing_fields": missing_in_b,
            "extra_fields": extra_in_b,
            "type_changes": type_changes,
            "breaking_changes": breaking_changes,
            "summary": {
                "total_source_fields": len(paths_a),
                "total_target_fields": len(paths_b),
                "common_fields": len(common_paths),
                "breaking_changes_count": len(breaking_changes)
            }
        }
