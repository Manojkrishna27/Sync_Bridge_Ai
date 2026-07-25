from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class ExecutionMetrics(BaseModel):
    __tablename__ = 'execution_metrics'

    correlation_id = Column(String(64), nullable=False, index=True)
    trace_id = Column(String(64), nullable=True, index=True)
    client_id = Column(String(36), ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    integration_id = Column(String(36), ForeignKey('integrations.id', ondelete='CASCADE'), nullable=False, index=True)

    db_time_ms = Column(Float, nullable=False, default=0.0)
    cache_time_ms = Column(Float, nullable=False, default=0.0)
    parsing_time_ms = Column(Float, nullable=False, default=0.0)
    validation_time_ms = Column(Float, nullable=False, default=0.0)
    ai_time_ms = Column(Float, nullable=False, default=0.0)
    transformation_time_ms = Column(Float, nullable=False, default=0.0)
    external_api_time_ms = Column(Float, nullable=False, default=0.0)
    total_time_ms = Column(Float, nullable=False, default=0.0)

    __table_args__ = (
        Index('idx_metrics_client_created', 'client_id', 'created_at'),
        Index('idx_metrics_integration_created', 'integration_id', 'created_at'),
        {'extend_existing': True}
    )

class CacheStatistics(BaseModel):
    __tablename__ = 'cache_statistics'

    namespace = Column(String(100), nullable=False, unique=True, index=True)
    hits = Column(Integer, nullable=False, default=0)
    misses = Column(Integer, nullable=False, default=0)
    hit_ratio = Column(Float, nullable=False, default=0.0)
    keys_count = Column(Integer, nullable=False, default=0)

    __table_args__ = ({'extend_existing': True},)

class RateLimitLogs(BaseModel):
    __tablename__ = 'rate_limit_logs'

    scope = Column(String(50), nullable=False) # GLOBAL, CLIENT, API_KEY, USER, IP, ENDPOINT
    scope_id = Column(String(255), nullable=False, index=True)
    client_id = Column(String(36), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    endpoint = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default='ALLOWED') # ALLOWED, REJECTED

    __table_args__ = (
        Index('idx_ratelimit_scope_status', 'scope', 'status'),
        {'extend_existing': True}
    )

class ConnectorHealth(BaseModel):
    __tablename__ = 'connector_health'

    connector_name = Column(String(100), nullable=False, unique=True, index=True)
    status = Column(String(50), nullable=False, default='HEALTHY') # HEALTHY, DEGRADED, CRITICAL, OFFLINE
    total_requests = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    failure_count = Column(Integer, nullable=False, default=0)
    avg_latency_ms = Column(Float, nullable=False, default=0.0)
    slowest_ms = Column(Float, nullable=False, default=0.0)
    fastest_ms = Column(Float, nullable=False, default=0.0)
    availability_pct = Column(Float, nullable=False, default=100.0)
    last_check_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = ({'extend_existing': True},)

class SystemAlert(BaseModel):
    __tablename__ = 'system_alerts'

    title = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False, default='WARNING') # WARNING, CRITICAL
    category = Column(String(100), nullable=False) # HIGH_FAILURE_RATE, SLOW_LATENCY, CONNECTOR_OFFLINE, RATE_LIMIT_ABUSE
    message = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default='ACTIVE') # ACTIVE, ACKNOWLEDGED, RESOLVED
    suppressed_until = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('idx_alert_status_sev', 'status', 'severity'),
        {'extend_existing': True}
    )

class PerformanceSnapshot(BaseModel):
    __tablename__ = 'performance_snapshots'

    rpm = Column(Float, nullable=False, default=0.0)
    success_rate = Column(Float, nullable=False, default=100.0)
    failure_rate = Column(Float, nullable=False, default=0.0)
    avg_latency = Column(Float, nullable=False, default=0.0)
    cache_hit_ratio = Column(Float, nullable=False, default=0.0)

    __table_args__ = ({'extend_existing': True},)
