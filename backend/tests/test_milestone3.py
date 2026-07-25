import pytest
import uuid
from app import create_app
from app.core.extensions import db
from app.services.client_service import ClientService
from app.services.integration_service import IntegrationService
from app.services.api_key_service import APIKeyService
from app.services.audit_log_service import AuditLogService
from app.connectors import get_connector, RESTConnector, SOAPConnector

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

def test_connectors_framework():
    rest = get_connector('REST')
    assert isinstance(rest, RESTConnector)
    assert rest.validate({"url": "https://api.example.com"}) is True

    soap = get_connector('SOAP')
    assert isinstance(soap, SOAPConnector)
    assert soap.validate({"wsdl_url": "https://api.example.com/soap?wsdl"}) is True

def test_client_service_lifecycle(app_instance):
    service = ClientService()
    client = service.create_client({
        "name": "Acme Test Corp",
        "industry": "Fintech",
        "settings": {"timezone": "EST"}
    }, user_id="test_user_1")

    assert client.id is not None
    assert client.name == "Acme Test Corp"
    assert client.settings.timezone == "EST"

    # Soft Delete test
    archived = service.archive_client(client.id, user_id="test_user_1")
    assert archived.status == 'Inactive'
    assert archived.deleted_at is not None

def test_integration_versioning_and_rollback(app_instance):
    client_svc = ClientService()
    client = client_svc.create_client({"name": "Test Client"}, user_id="user1")

    int_svc = IntegrationService()
    integration = int_svc.create_integration(
        client_id=client.id,
        data={
            "name": "SAP to Salesforce Sync",
            "source_system": "SAP",
            "destination_system": "Salesforce",
            "source_protocol": "REST",
            "destination_protocol": "REST",
            "config": {"mapping": {"v": 1}}
        },
        user_id="user1"
    )

    assert integration.version == 1

    # Update config (should bump version to 2)
    updated = int_svc.update_integration(
        integration.id,
        data={"config": {"mapping": {"v": 2}}, "change_notes": "Bump to v2"},
        user_id="user1"
    )
    assert updated.version == 2

    # Rollback to version 1
    rolled_back = int_svc.rollback_integration(integration.id, version_number=1, user_id="user1")
    assert rolled_back.version == 3
    assert rolled_back.config == {"mapping": {"v": 1}}

def test_api_key_hashing_and_rotation(app_instance):
    client_svc = ClientService()
    client = client_svc.create_client({"name": "Key Client"}, user_id="user1")

    key_svc = APIKeyService()
    key, raw_secret = key_svc.generate_key(client_id=client.id, name="Test Key", days_valid=30, user_id="user1")

    assert raw_secret.startswith("sb_live_")
    assert key.key_hash != raw_secret  # Hashed in DB

    # Key Rotation
    new_key, new_raw_secret = key_svc.rotate_key(key.id, user_id="user1")
    assert new_raw_secret != raw_secret
    assert key_svc.api_key_repo.get_by_id(key.id).status == 'Revoked'
