import pytest
import uuid
import os
from app import create_app
from app.core.extensions import db
from app.connectors import ConnectorRegistry, get_connector, RESTConnector, SOAPConnector
from app.integration_engine.protocol_detector import ProtocolDetector
from app.integration_engine.payload_parser import PayloadParser
from app.integration_engine.schema_validator import SchemaValidator
from app.integration_engine.mapping_rules_engine import MappingRulesEngine
from app.integration_engine.transformation_engine import TransformationEngine
from app.integration_engine.execution_manager import ExecutionManager
from app.services.client_service import ClientService
from app.services.integration_service import IntegrationService

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

def test_connector_registry():
    protocols = ConnectorRegistry.list_supported_protocols()
    assert "REST" in protocols
    assert "SOAP" in protocols
    assert "XML" in protocols
    assert "JSON" in protocols
    assert "CSV" in protocols
    assert "GRAPHQL" in protocols
    assert "GRPC" in protocols

    conn = get_connector("GRPC")
    assert conn.validate({"proto_schema": "service.proto"}) is True

def test_protocol_detector():
    soap_xml = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Body/></soapenv:Envelope>'
    assert ProtocolDetector.detect(soap_xml) == "SOAP"

    plain_xml = '<?xml version="1.0"?><root><item>1</item></root>'
    assert ProtocolDetector.detect(plain_xml) == "XML"

    json_str = '{"name": "Acme", "status": "Active"}'
    assert ProtocolDetector.detect(json_str) == "JSON"

    csv_str = "id,name,email\n1,John,john@example.com"
    assert ProtocolDetector.detect(csv_str) == "CSV"

def test_payload_parser_soap_and_xml():
    soap_xml = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Body><Customer><Id>123</Id><Name>Alice</Name></Customer></soapenv:Body></soapenv:Envelope>'
    parsed = PayloadParser.parse(soap_xml, "SOAP")
    assert "Customer" in parsed
    assert parsed["Customer"]["Name"] == "Alice"

def test_schema_validator():
    schema = {
        "required": ["email", "user_id"],
        "properties": {
            "email": {"type": "string", "format": "email"},
            "user_id": {"type": "string", "format": "uuid"},
            "age": {"type": "integer"},
            "role": {"type": "string", "enum": ["ADMIN", "USER"]}
        }
    }

    valid_payload = {
        "email": "user@example.com",
        "user_id": str(uuid.uuid4()),
        "age": 30,
        "role": "ADMIN"
    }

    is_valid, errors = SchemaValidator.validate(valid_payload, schema)
    assert is_valid is True
    assert len(errors) == 0

    invalid_payload = {
        "email": "invalid-email-address",
        "user_id": "not-a-uuid",
        "role": "INVALID_ROLE"
    }

    is_valid, errors = SchemaValidator.validate(invalid_payload, schema)
    assert is_valid is False
    assert len(errors) >= 3

def test_mapping_rules_engine():
    source_data = {
        "customer_name": "acme inc",
        "raw_status": "1",
        "address": {"city": "New York", "zip": "10001"}
    }

    rules_config = {
        "mappings": {
            "customer_name": "company_name",
            "address.city": "location.city"
        },
        "lookups": {
            "raw_status": {"1": "ACTIVE", "0": "INACTIVE"}
        },
        "transformations": {
            "company_name": "uppercase"
        },
        "defaults": {
            "country": "USA"
        }
    }

    transformed = MappingRulesEngine.apply_rules(source_data, rules_config)
    assert transformed["company_name"] == "ACME INC"
    assert transformed["location"]["city"] == "New York"
    assert transformed["raw_status"] == "ACTIVE"
    assert transformed["country"] == "USA"

def test_execution_manager_preview_and_execute(app_instance):
    client_svc = ClientService()
    client = client_svc.create_client({"name": "Test Exec Client"}, user_id="user1")

    int_svc = IntegrationService()
    integration = int_svc.create_integration(
        client_id=client.id,
        data={
            "name": "Legacy SOAP to REST Pipeline",
            "source_system": "Legacy SOAP",
            "destination_system": "REST API",
            "source_protocol": "SOAP",
            "destination_protocol": "REST",
            "config": {
                "schema": {"required": ["Customer"]},
                "mapping_config": {
                    "mappings": {
                        "Customer.Name": "customer_name"
                    }
                }
            }
        },
        user_id="user1"
    )

    manager = ExecutionManager()
    soap_input = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Body><Customer><Name>Enterprise Corp</Name></Customer></soapenv:Body></soapenv:Envelope>'

    # 1. Preview Mode Test
    resp_preview = manager.run_pipeline(integration, soap_input, mode="PREVIEW")
    assert resp_preview.status_code == 200
    json_data = resp_preview.get_json()
    assert json_data["data"]["preview"] is True
    assert json_data["data"]["transformed_payload"]["customer_name"] == "Enterprise Corp"

    # 2. Execution Mode Test
    resp_exec = manager.run_pipeline(integration, soap_input, mode="EXECUTE")
    assert resp_exec.status_code == 200
    exec_json = resp_exec.get_json()
    assert exec_json["success"] is True
