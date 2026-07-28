import pytest
import json
from app import create_app
from app.core.extensions import db
from app.models.role import Role, Permission, RolePermission
from app.models.user import User
from app.core.security import hash_password

@pytest.fixture
def client_app():
    app = create_app(test_config={
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            # Seed Admin Role & Permissions
            admin_role = Role(id="role-admin-1", name="Admin", description="Admin Role")
            db.session.add(admin_role)

            perms = [
                Permission(id="p1", name="manage_users"),
                Permission(id="p2", name="manage_clients"),
                Permission(id="p3", name="manage_integrations"),
                Permission(id="p4", name="execute_integrations"),
                Permission(id="p5", name="view_dashboard"),
                Permission(id="p6", name="use_copilot")
            ]
            for p in perms:
                db.session.add(p)
            db.session.commit()

            for p in perms:
                db.session.add(RolePermission(role_id=admin_role.id, permission_id=p.id))

            # Seed Admin User
            admin_user = User(
                id="usr-admin-1",
                email="admin@syncbridge.ai",
                password_hash=hash_password("Admin123!"),
                first_name="Admin",
                last_name="User",
                role_id=admin_role.id,
                is_active=True,
                is_locked=False
            )
            db.session.add(admin_user)
            db.session.commit()

            yield client

            db.session.remove()
            db.drop_all()

def test_full_e2e_integration_flow(client_app):
    # Step 1: Login & obtain JWT token
    login_res = client_app.post('/api/v1/auth/login', json={
        'email': 'admin@syncbridge.ai',
        'password': 'Admin123!'
    })
    assert login_res.status_code == 200
    token_data = login_res.get_json()
    assert 'access_token' in token_data
    access_token = token_data['access_token']
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-User-ID': 'usr-admin-1'
    }

    # Step 2: Create a Client Tenant
    client_res = client_app.post('/api/v1/clients', headers=headers, json={
        'name': 'Acme Global Fintech',
        'industry': 'Financial Services',
        'contact_email': 'contact@acme-fintech.com',
        'subscription_plan': 'Enterprise'
    })
    assert client_res.status_code == 201
    client_id = client_res.get_json()['client_id']

    # Step 3: Generate API Key for Client Tenant
    key_res = client_app.post('/api/v1/apikeys', headers=headers, json={
        'client_id': client_id,
        'name': 'Production Stripe Integration Key',
        'days_valid': 30
    })
    assert key_res.status_code == 201
    assert 'raw_api_key' in key_res.get_json()

    # Step 4: Create Integration Pipeline (SOAP XML -> REST JSON)
    integ_res = client_app.post('/api/v1/integrations', headers=headers, json={
        'client_id': client_id,
        'name': 'E2E Payment Sync Pipeline',
        'source_system': 'Legacy Core Banking',
        'destination_system': 'Cloud Payment Gateway',
        'source_protocol': 'SOAP',
        'destination_protocol': 'REST',
        'environment': 'Production',
        'config': {
            'mapping_rules': [
                {'source': 'CustomerId', 'target': 'customer_id'},
                {'source': 'EmailAddress', 'target': 'email'}
            ]
        }
    })
    assert integ_res.status_code == 201
    integration_id = integ_res.get_json()['id']

    # Step 5: Execute Payload Protocol Translation
    soap_payload = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
       <soapenv:Body>
          <CustomerRecord>
             <CustomerId>CUST-99182</CustomerId>
             <EmailAddress>finance@acme.com</EmailAddress>
          </CustomerRecord>
       </soapenv:Body>
    </soapenv:Envelope>"""

    exec_res = client_app.post(f'/api/v1/executions/integrations/{integration_id}/execute', headers=headers, json={
        'payload': soap_payload
    })
    assert exec_res.status_code in [200, 201]
    exec_data = exec_res.get_json()
    assert exec_data.get('success') is True

    # Step 6: Ask AI Copilot for Schema Analysis
    copilot_res = client_app.post('/api/v1/copilot/chat', headers=headers, json={
        'query': 'Analyze schema mapping for CustomerId to customer_id',
        'user_id': 'usr-admin-1',
        'client_id': client_id
    })
    assert copilot_res.status_code == 200
    assert 'conversation_id' in copilot_res.get_json()

    # Step 7: Inspect Cryptographic Audit Logs
    audit_res = client_app.get('/api/v1/audit-logs', headers=headers)
    assert audit_res.status_code == 200
    audit_logs = audit_res.get_json().get('data', [])
    assert len(audit_logs) > 0
