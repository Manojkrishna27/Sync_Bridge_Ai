import pytest
import os
import subprocess
from app import create_app
from app.core.extensions import db

@pytest.fixture
def client_app():
    app = create_app(test_config={
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_health_check_endpoint(client_app):
    res = client_app.get('/api/v1/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] in ["HEALTHY", "DEGRADED", "CRITICAL"]

def test_security_headers(client_app):
    res = client_app.get('/api/v1/health')
    assert res.headers.get('X-Frame-Options') == 'SAMEORIGIN'
    assert res.headers.get('X-Content-Type-Options') == 'nosniff'
    assert res.headers.get('X-XSS-Protection') == '1; mode=block'
    assert 'Content-Security-Policy' in res.headers

def test_prometheus_metrics_endpoint(client_app):
    res = client_app.get('/api/v1/monitoring/prometheus')
    assert res.status_code == 200
    assert "syncbridge_rpm" in res.get_data(as_text=True)

def test_backup_and_restore_scripts_exist():
    assert os.path.exists("scripts/backup.sh")
    assert os.path.exists("scripts/restore.sh")
    assert os.path.exists("docker-compose.prod.yml")
    assert os.path.exists("docker-compose.dev.yml")
