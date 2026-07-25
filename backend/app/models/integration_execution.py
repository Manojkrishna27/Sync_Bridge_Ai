from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import BaseModel

class IntegrationExecution(BaseModel):
    __tablename__ = 'integration_executions'

    correlation_id = Column(String(64), nullable=False, index=True)
    client_id = Column(String(36), ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    integration_id = Column(String(36), ForeignKey('integrations.id', ondelete='CASCADE'), nullable=False, index=True)
    
    status = Column(String(50), nullable=False, default='PENDING', index=True) # PENDING, SUCCESS, FAILED, VALIDATION_ERROR
    protocol = Column(String(50), nullable=False) # SOAP, XML, JSON, CSV, GraphQL, SFTP
    execution_mode = Column(String(50), nullable=False, default='EXECUTE') # EXECUTE, PREVIEW
    payload_size = Column(Integer, nullable=False, default=0)

    # Duration metrics (ms)
    parsing_time_ms = Column(Float, nullable=False, default=0.0)
    validation_time_ms = Column(Float, nullable=False, default=0.0)
    transformation_time_ms = Column(Float, nullable=False, default=0.0)
    request_time_ms = Column(Float, nullable=False, default=0.0)
    total_time_ms = Column(Float, nullable=False, default=0.0)

    # Stage Timestamps
    received_at = Column(DateTime, default=datetime.utcnow)
    parsed_at = Column(DateTime, nullable=True)
    validated_at = Column(DateTime, nullable=True)
    transformed_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    response_received_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Payload Tracing & DLQ Readiness
    request_payload = Column(Text, nullable=True)
    response_payload = Column(Text, nullable=True)
    dlq_eligible = Column(Boolean, nullable=False, default=False, index=True)

    # Relationships
    logs = relationship("ExecutionLog", back_populates="execution", cascade="all, delete-orphan")
    errors = relationship("ExecutionError", back_populates="execution", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_exec_client_status', 'client_id', 'status'),
        Index('idx_exec_integration_created', 'integration_id', 'created_at'),
        {'extend_existing': True}
    )

class ExecutionLog(BaseModel):
    __tablename__ = 'execution_logs'

    execution_id = Column(String(36), ForeignKey('integration_executions.id', ondelete='CASCADE'), nullable=False, index=True)
    step_name = Column(String(100), nullable=False) # e.g. PARSING, VALIDATION, TRANSFORMATION, DISPATCH
    log_level = Column(String(20), nullable=False, default='INFO')
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)

    # Relationships
    execution = relationship("IntegrationExecution", back_populates="logs")

    __table_args__ = (
        Index('idx_log_execution_step', 'execution_id', 'step_name'),
        {'extend_existing': True}
    )

class ExecutionError(BaseModel):
    __tablename__ = 'execution_errors'

    execution_id = Column(String(36), ForeignKey('integration_executions.id', ondelete='CASCADE'), nullable=False, index=True)
    error_code = Column(String(50), nullable=False, index=True) # e.g. ERR_PARSER_001, ERR_VAL_002
    category = Column(String(50), nullable=False, default='SYSTEM_ERROR') # PARSE_ERROR, VALIDATION_ERROR, TRANSFORMATION_ERROR, NETWORK_ERROR
    message = Column(Text, nullable=False)
    technical_details = Column(Text, nullable=True)
    suggested_resolution = Column(Text, nullable=True)

    # Relationships
    execution = relationship("IntegrationExecution", back_populates="errors")

    __table_args__ = (
        Index('idx_err_execution_code', 'execution_id', 'error_code'),
        {'extend_existing': True}
    )
