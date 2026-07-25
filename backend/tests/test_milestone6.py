import pytest
import time
import uuid
import os
from app import create_app
from app.core.extensions import db
from app.core.cache import RedisCacheService
from app.core.rate_limiter import TokenBucketRateLimiter
from app.workers.job_manager import WorkerManager, JobPriority
from app.services.monitoring_service import MonitoringService
from app.services.alert_service import AlertService
from app.models.monitoring_model import SystemAlert, ExecutionMetrics

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

def test_redis_cache_service():
    cache = RedisCacheService()
    
    # Test Set and Get
    cache.set("test_ns", "key1", {"data": "value1"}, ttl=60, tags=["tagA"])
    val = cache.get("test_ns", "key1")
    assert val == {"data": "value1"}

    # Test Compression
    large_payload = {"items": ["item_" + str(i) for i in range(1000)]}
    cache.set("test_ns", "key_compressed", large_payload, ttl=60, compress=True)
    val_comp = cache.get("test_ns", "key_compressed")
    assert len(val_comp["items"]) == 1000

    # Test Namespace Telemetry
    stats = cache.get_namespace_statistics()
    assert "test_ns" in stats
    assert stats["test_ns"]["hits"] >= 2

def test_token_bucket_rate_limiter():
    limiter = TokenBucketRateLimiter()
    limiter.update_scope_config("CLIENT", capacity=2, refill_rate=0.1)

    # 1. First 2 requests pass
    allowed1, _ = limiter.evaluate_request(client_id="client_123")
    allowed2, _ = limiter.evaluate_request(client_id="client_123")
    assert allowed1 is True
    assert allowed2 is True

    # 3rd request blocked
    allowed3, info = limiter.evaluate_request(client_id="client_123")
    assert allowed3 is False
    assert info["scope"] == "CLIENT"

def test_worker_manager_priority_queues():
    manager = WorkerManager()

    results = []

    def job_low(): results.append("LOW")
    def job_critical(): results.append("CRITICAL")

    manager.enqueue_job(job_low, priority=JobPriority.LOW)
    manager.enqueue_job(job_critical, priority=JobPriority.CRITICAL)

    # Process first job (CRITICAL should bypass LOW)
    res1 = manager.process_next_job()
    assert results[0] == "CRITICAL"

    res2 = manager.process_next_job()
    assert results[1] == "LOW"

def test_alert_service_and_audit(app_instance):
    service = AlertService()

    alert = service.trigger_alert(
        title="Test Failure Alert",
        severity="WARNING",
        category="HIGH_FAILURE_RATE",
        message="System failure rate exceeded"
    )

    assert alert.id is not None
    assert alert.status == 'ACTIVE'

    # Suppression test
    suppressed = service.trigger_alert(
        title="Duplicate Alert",
        severity="WARNING",
        category="HIGH_FAILURE_RATE",
        message="System failure rate exceeded"
    )
    assert suppressed is None

    # Acknowledgement test
    ack = service.acknowledge_alert(alert.id, user_id="user1")
    assert ack.status == 'ACKNOWLEDGED'

def test_monitoring_service_health(app_instance):
    mon_svc = MonitoringService()
    health = mon_svc.get_system_health()

    assert health["status"] in ["HEALTHY", "DEGRADED", "CRITICAL"]
    assert health["services"]["database"] == "UP"
    assert len(health["connectors"]) > 0
