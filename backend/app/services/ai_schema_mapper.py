import hashlib
import json
from typing import Dict, Any, List
from app.ai.providers import get_ai_provider
from app.services.schema_analyzer import SchemaAnalyzer
from app.core.logger import get_logger

logger = get_logger()

class AISchemaMapper:
    """
    Hybrid AI Schema Mapper.
    Combines Saved Mappings -> Templates -> Heuristic Matcher -> AI Semantic Matcher -> Manual fallback,
    with Redis caching and feedback logging.
    """

    def __init__(self, ai_provider=None):
        self.provider = ai_provider or get_ai_provider("auto")

    def generate_hybrid_mappings(
        self,
        source_schema_tree: dict,
        target_schema_tree: dict,
        existing_rules: list = None,
        template_rules: list = None
    ) -> List[Dict[str, Any]]:
        
        flat_source = SchemaAnalyzer.extract_flat_fields(source_schema_tree)
        flat_target = SchemaAnalyzer.extract_flat_fields(target_schema_tree)

        suggestions = []
        mapped_target_paths = set()

        # 1. Existing Saved Mappings Priority
        if existing_rules:
            for rule in existing_rules:
                t_path = rule.get("target_path")
                s_path = rule.get("source_path")
                if t_path and s_path:
                    suggestions.append({
                        "source_field": s_path,
                        "target_field": t_path,
                        "confidence_score": 1.0,
                        "reason": "Pre-existing saved client mapping",
                        "strategy_used": "SAVED_MAPPING",
                        "suggested_transformation": rule.get("rule_type")
                    })
                    mapped_target_paths.add(t_path)

        # 2. Template Mappings Priority
        if template_rules:
            for rule in template_rules:
                t_path = rule.get("target_path")
                s_path = rule.get("source_path")
                if t_path and s_path and t_path not in mapped_target_paths:
                    suggestions.append({
                        "source_field": s_path,
                        "target_field": t_path,
                        "confidence_score": 0.95,
                        "reason": "Organization template rule",
                        "strategy_used": "TEMPLATE",
                        "suggested_transformation": rule.get("rule_type")
                    })
                    mapped_target_paths.add(t_path)

        # Filter unmapped fields for AI / Heuristic analysis
        unmapped_source = [f for f in flat_source if not any(s['source_field'] == f['path'] for s in suggestions)]
        unmapped_target = [f for f in flat_target if f['path'] not in mapped_target_paths]

        if unmapped_source and unmapped_target:
            # 3. AI / Heuristic Provider Execution
            ai_results = self.provider.generate_mapping_suggestions(unmapped_source, unmapped_target)
            for res in ai_results:
                t_path = res.get("target_field")
                if t_path and t_path not in mapped_target_paths:
                    res["strategy_used"] = "AI_MATCH" if res.get("confidence_score", 0) > 0.85 else "HEURISTIC"
                    suggestions.append(res)
                    mapped_target_paths.add(t_path)

        return suggestions
