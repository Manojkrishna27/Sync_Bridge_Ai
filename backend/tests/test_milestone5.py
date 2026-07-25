import pytest
import uuid
import os
from app import create_app
from app.core.extensions import db
from app.models.schema_model import Schema, SchemaVersion, Mapping, MappingVersion
from app.services.schema_analyzer import SchemaAnalyzer
from app.services.schema_comparator import SchemaComparator
from app.ai.providers import get_ai_provider, MockAIProvider
from app.services.ai_schema_mapper import AISchemaMapper
from app.services.mapping_service import MappingService
from app.services.client_service import ClientService

@pytest.fixture
def app_instance():
    app = create_app(test_config={
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

def test_schema_analyzer_parsing():
    json_schema = '{"name": "Alice", "contact": {"email": "alice@example.com"}}'
    tree_json = SchemaAnalyzer.analyze(json_schema, "JSON")
    assert tree_json["root_type"] == "object"
    assert len(tree_json["fields"]) == 2

    xml_schema = '<root><user><id>101</id><email>user@test.com</email></user></root>'
    tree_xml = SchemaAnalyzer.analyze(xml_schema, "XML")
    assert tree_xml["root_type"] == "xml_element"

    csv_schema = "id,name,email\n1,Bob,bob@example.com"
    tree_csv = SchemaAnalyzer.analyze(csv_schema, "CSV")
    assert len(tree_csv["fields"]) == 3

def test_schema_comparator():
    schema_a = {
        "fields": [
            {"name": "id", "type": "integer", "required": True},
            {"name": "email", "type": "string", "required": True},
            {"name": "age", "type": "integer", "required": False}
        ]
    }

    schema_b = {
        "fields": [
            {"name": "id", "type": "string", "required": True}, # Type changed (integer -> string)
            {"name": "email", "type": "string", "required": True},
            {"name": "location", "type": "string", "required": False} # Missing age, extra location
        ]
    }

    diff = SchemaComparator.compare(schema_a, schema_b)
    assert diff["compatibility_score"] < 100.0
    assert "location" in diff["extra_fields"]
    assert "age" in diff["missing_fields"]
    assert len(diff["type_changes"]) == 1
    assert diff["is_compatible"] is False  # Type mutation is breaking

def test_ai_provider_and_hybrid_mapper():
    provider = get_ai_provider("mock")
    assert isinstance(provider, MockAIProvider)

    source_tree = {"fields": [{"name": "customer_name", "type": "string"}, {"name": "email_address", "type": "string"}]}
    target_tree = {"fields": [{"name": "fullName", "type": "string"}, {"name": "email", "type": "string"}]}

    mapper = AISchemaMapper(provider)
    suggestions = mapper.generate_hybrid_mappings(source_tree, target_tree)

    assert len(suggestions) >= 2
    matched_targets = [s["target_field"] for s in suggestions]
    assert "fullName" in matched_targets
    assert "email" in matched_targets

def test_mapping_service_lifecycle_and_rollback(app_instance):
    client_svc = ClientService()
    client = client_svc.create_client({"name": "Studio Client"}, user_id="user1")

    map_svc = MappingService()

    # 1. Upload Schemas
    valid_soap_xml = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Body><CustName>Acme</CustName></soapenv:Body></soapenv:Envelope>'
    s_src = map_svc.upload_schema(client.id, "Legacy SOAP Schema", "SOAP", valid_soap_xml)
    s_tgt = map_svc.upload_schema(client.id, "Target REST Schema", "JSON", '{"fullName": "Acme"}')

    assert s_src.id is not None
    assert s_tgt.id is not None

    # 2. Save Mapping v1
    rules_v1 = [{"source_path": "CustName", "target_path": "fullName", "rule_type": "STATIC"}]
    mapping = map_svc.save_mapping(
        client_id=client.id,
        name="SOAP to REST User Sync",
        rules=rules_v1,
        source_schema_id=s_src.id,
        target_schema_id=s_tgt.id,
        user_id="user1"
    )
    assert mapping.version == 1

    # 3. Update Mapping v2
    rules_v2 = [
        {"source_path": "CustName", "target_path": "fullName", "rule_type": "STATIC"},
        {"source_path": "Email", "target_path": "email", "rule_type": "STATIC"}
    ]
    updated = map_svc.save_mapping(
        client_id=client.id,
        name="SOAP to REST User Sync",
        rules=rules_v2,
        mapping_id=mapping.id,
        user_id="user1"
    )
    assert updated.version == 2
    assert len(updated.rules) == 2

    # 4. Rollback to Version 1
    rolled_back = map_svc.rollback_mapping(mapping.id, version_number=1, user_id="user1")
    assert rolled_back.version == 3
    assert len(rolled_back.rules) == 1
    assert rolled_back.rules[0].target_path == "fullName"

def test_mapping_rule_validation():
    map_svc = MappingService()

    invalid_rules = [
        {"source_path": "user.id", "target_path": "user.id"}, # Circular
        {"source_path": "fieldA", "target_path": "fullName"},
        {"source_path": "fieldB", "target_path": "fullName"}  # Duplicate target
    ]

    val_res = map_svc.validate_mapping_rules(invalid_rules)
    assert val_res["valid"] is False
    assert val_res["errors_count"] == 1
    assert val_res["warnings_count"] == 1
