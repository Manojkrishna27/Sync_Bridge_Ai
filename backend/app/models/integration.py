from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class Integration(BaseModel):
    __tablename__ = 'integrations'

    client_id = Column(String(36), ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    source_system = Column(String(100), nullable=False, index=True)
    destination_system = Column(String(100), nullable=False, index=True)
    source_protocol = Column(String(50), nullable=False) # REST, SOAP, XML, CSV, GraphQL, SFTP
    destination_protocol = Column(String(50), nullable=False)
    integration_type = Column(String(100), nullable=True)
    environment = Column(String(50), nullable=False, default='Development', index=True) # Development, Staging, Production
    status = Column(String(50), nullable=False, default='Inactive', index=True) # Active, Inactive
    version = Column(Integer, nullable=False, default=1)
    health_score = Column(Integer, nullable=False, default=100)
    health_status = Column(String(50), nullable=False, default='Healthy', index=True) # Healthy, Warning, Critical, Offline

    # Execution Statistics
    total_executions = Column(Integer, nullable=False, default=0)
    successful_executions = Column(Integer, nullable=False, default=0)
    failed_executions = Column(Integer, nullable=False, default=0)
    average_execution_time = Column(Float, nullable=False, default=0.0)
    last_execution_time = Column(DateTime, nullable=True)

    # Filtering & Configuration
    tags = Column(JSON, nullable=True, default=list) # e.g. ["Finance", "REST"]
    config = Column(JSON, nullable=True)
    created_by = Column(String(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Relationships
    client = relationship("Client", back_populates="integrations")
    versions = relationship("IntegrationVersion", back_populates="integration", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_integration_client_status', 'client_id', 'status', 'deleted_at'),
        Index('idx_integration_client_env', 'client_id', 'environment', 'deleted_at'),
        Index('idx_integration_protocols', 'source_protocol', 'destination_protocol'),
    )
