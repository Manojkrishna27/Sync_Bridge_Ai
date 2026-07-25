import uuid
from typing import Dict, Any, List, Optional, Tuple
from app.core.extensions import db
from app.models.schema_model import (
    Schema, SchemaVersion, Mapping, MappingRule, MappingVersion, AISuggestion, TransformationTemplate
)
from app.services.schema_analyzer import SchemaAnalyzer
from app.services.schema_comparator import SchemaComparator
from app.services.ai_schema_mapper import AISchemaMapper
from app.integration_engine.mapping_rules_engine import MappingRulesEngine
from app.core.logger import get_logger

logger = get_logger()

DEFAULT_TEMPLATES = [
    {
        "name": "SAP to Salesforce",
        "category": "ERP Sync",
        "description": "Standard mapping template for SAP Account/Contact payloads into Salesforce CRM objects.",
        "rules": [
            {"source_path": "KUNNR", "target_path": "AccountNumber", "rule_type": "STATIC"},
            {"source_path": "NAME1", "target_path": "Name", "rule_type": "STATIC"},
            {"source_path": "STRAS", "target_path": "BillingStreet", "rule_type": "STATIC"},
            {"source_path": "ORT01", "target_path": "BillingCity", "rule_type": "STATIC"},
            {"source_path": "PSTLZ", "target_path": "BillingPostalCode", "rule_type": "STATIC"},
            {"source_path": "LAND1", "target_path": "BillingCountry", "rule_type": "STATIC"}
        ]
    },
    {
        "name": "SOAP to REST JSON",
        "category": "Legacy Conversion",
        "description": "Unwraps legacy SOAP Request envelopes into modern REST JSON structures.",
        "rules": [
            {"source_path": "GetCustomerRequest.CustomerId", "target_path": "id", "rule_type": "STATIC"},
            {"source_path": "GetCustomerRequest.Email", "target_path": "email", "rule_type": "STATIC"}
        ]
    }
]

class MappingService:
    """Service managing Schemas, Visual Mappings, Templates, Validation, and Rollbacks."""

    def __init__(self):
        self.ai_mapper = AISchemaMapper()

    # --- Schema Methods ---
    def upload_schema(self, client_id: str, name: str, format_type: str, raw_schema: str, description: str = None) -> Schema:
        parsed_tree = SchemaAnalyzer.analyze(raw_schema, format_type)
        schema_id = str(uuid.uuid4())
        
        schema = Schema(
            id=schema_id,
            client_id=client_id,
            name=name,
            format=format_type.upper(),
            description=description
        )
        db.session.add(schema)

        version = SchemaVersion(
            id=str(uuid.uuid4()),
            schema_id=schema_id,
            version_number=1,
            raw_schema=raw_schema,
            parsed_tree=parsed_tree,
            change_description="Initial schema upload"
        )
        db.session.add(version)
        db.session.commit()

        return schema

    def get_schema(self, schema_id: str) -> Schema:
        schema = Schema.query.filter_by(id=schema_id, deleted_at=None).first()
        if not schema:
            raise ValueError("Schema record not found")
        return schema

    def compare_schemas(self, schema_a_id: str, schema_b_id: str) -> dict:
        s_a = self.get_schema(schema_a_id)
        s_b = self.get_schema(schema_b_id)

        v_a = SchemaVersion.query.filter_by(schema_id=s_a.id).order_by(SchemaVersion.version_number.desc()).first()
        v_b = SchemaVersion.query.filter_by(schema_id=s_b.id).order_by(SchemaVersion.version_number.desc()).first()

        return SchemaComparator.compare(v_a.parsed_tree, v_b.parsed_tree)

    # --- Mapping Methods ---
    def generate_ai_suggestions(self, source_schema_id: str, target_schema_id: str, mapping_id: str = None) -> List[dict]:
        s_src = self.get_schema(source_schema_id)
        s_tgt = self.get_schema(target_schema_id)

        v_src = SchemaVersion.query.filter_by(schema_id=s_src.id).order_by(SchemaVersion.version_number.desc()).first()
        v_tgt = SchemaVersion.query.filter_by(schema_id=s_tgt.id).order_by(SchemaVersion.version_number.desc()).first()

        existing_rules = []
        if mapping_id:
            m = Mapping.query.filter_by(id=mapping_id).first()
            if m:
                existing_rules = [{"source_path": r.source_path, "target_path": r.target_path, "rule_type": r.rule_type} for r in m.rules]

        suggestions = self.ai_mapper.generate_hybrid_mappings(v_src.parsed_tree, v_tgt.parsed_tree, existing_rules)

        if mapping_id:
            # Persist AI Suggestions for Feedback Tracking
            for sug in suggestions:
                db.session.add(AISuggestion(
                    id=str(uuid.uuid4()),
                    mapping_id=mapping_id,
                    source_field=sug.get("source_field"),
                    target_field=sug.get("target_field"),
                    confidence_score=sug.get("confidence_score", 0.0),
                    reason=sug.get("reason"),
                    suggested_rule={"type": sug.get("suggested_transformation")},
                    status="PENDING"
                ))
            db.session.commit()

        return suggestions

    def validate_mapping_rules(self, rules: List[dict], target_schema_id: str = None) -> dict:
        diagnostics = []

        seen_targets = set()
        seen_sources = set()

        for r in rules:
            src = r.get("source_path")
            tgt = r.get("target_path")

            # Circular Mapping Check
            if src == tgt:
                diagnostics.append({
                    "severity": "ERROR",
                    "code": "ERR_CIRCULAR",
                    "message": f"Circular mapping detected on path '{src}'"
                })

            # Duplicate Target Field Check
            if tgt in seen_targets:
                diagnostics.append({
                    "severity": "WARNING",
                    "code": "WARN_DUPLICATE_TARGET",
                    "message": f"Target path '{tgt}' is mapped multiple times"
                })
            else:
                seen_targets.add(tgt)

            seen_sources.add(src)

        errors_count = sum(1 for d in diagnostics if d["severity"] == "ERROR")
        warnings_count = sum(1 for d in diagnostics if d["severity"] == "WARNING")

        return {
            "valid": errors_count == 0,
            "errors_count": errors_count,
            "warnings_count": warnings_count,
            "diagnostics": diagnostics
        }

    def save_mapping(
        self,
        client_id: str,
        name: str,
        rules: List[dict],
        source_schema_id: str = None,
        target_schema_id: str = None,
        integration_id: str = None,
        mapping_id: str = None,
        change_description: str = "Saved mapping update",
        user_id: str = None
    ) -> Mapping:

        if mapping_id:
            mapping = Mapping.query.filter_by(id=mapping_id, client_id=client_id).first()
            if not mapping:
                raise ValueError("Mapping not found")
            mapping.name = name
            mapping.version += 1
            # Delete existing rules to replace with snapshot
            MappingRule.query.filter_by(mapping_id=mapping.id).delete()
        else:
            mapping_id = str(uuid.uuid4())
            mapping = Mapping(
                id=mapping_id,
                client_id=client_id,
                integration_id=integration_id,
                name=name,
                source_schema_id=source_schema_id,
                target_schema_id=target_schema_id,
                version=1
            )
            db.session.add(mapping)

        # Create Mapping Rules
        rule_entities = []
        for r in rules:
            r_entity = MappingRule(
                id=str(uuid.uuid4()),
                mapping_id=mapping.id,
                source_path=r.get("source_path"),
                target_path=r.get("target_path"),
                rule_type=r.get("rule_type", "STATIC"),
                strategy_used=r.get("strategy_used", "MANUAL"),
                config=r.get("config")
            )
            db.session.add(r_entity)
            rule_entities.append(r)

        # Create Version Snapshot
        version_snapshot = MappingVersion(
            id=str(uuid.uuid4()),
            mapping_id=mapping.id,
            version_number=mapping.version,
            rules_snapshot=rules,
            created_by=user_id,
            change_description=change_description
        )
        db.session.add(version_snapshot)
        db.session.commit()

        return mapping

    def rollback_mapping(self, mapping_id: str, version_number: int, user_id: str = None) -> Mapping:
        mapping = Mapping.query.filter_by(id=mapping_id).first()
        if not mapping:
            raise ValueError("Mapping not found")

        v_target = MappingVersion.query.filter_by(mapping_id=mapping_id, version_number=version_number).first()
        if not v_target:
            raise ValueError(f"Mapping version {version_number} not found")

        # Rollback rules snapshot
        rules_snapshot = v_target.rules_snapshot

        return self.save_mapping(
            client_id=mapping.client_id,
            name=mapping.name,
            rules=rules_snapshot,
            source_schema_id=mapping.source_schema_id,
            target_schema_id=mapping.target_schema_id,
            integration_id=mapping.integration_id,
            mapping_id=mapping.id,
            change_description=f"Rolled back to version {version_number}",
            user_id=user_id
        )

    def simulate_mapping(self, source_payload: dict, rules: List[dict]) -> dict:
        mapping_config = {"mappings": {}}
        for r in rules:
            s_path = r.get("source_path")
            t_path = r.get("target_path")
            if s_path and t_path:
                mapping_config["mappings"][s_path] = t_path

        transformed = MappingRulesEngine.apply_rules(source_payload, mapping_config)
        return {
            "simulation": True,
            "source_payload": source_payload,
            "transformed_payload": transformed
        }

    # --- Template Methods ---
    def get_templates() -> List[dict]:
        templates = TransformationTemplate.query.all()
        if not templates:
            # Seed default templates
            for t_data in DEFAULT_TEMPLATES:
                t_obj = TransformationTemplate(
                    id=str(uuid.uuid4()),
                    name=t_data["name"],
                    category=t_data["category"],
                    description=t_data["description"],
                    rules=t_data["rules"]
                )
                db.session.add(t_obj)
            db.session.commit()
            templates = TransformationTemplate.query.all()

        return [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category,
                "description": t.description,
                "rules": t.rules
            } for t in templates
        ]
