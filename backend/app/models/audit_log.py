from sqlalchemy import Column, String, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class AuditLog(BaseModel):
    __tablename__ = 'audit_logs'

    correlation_id = Column(String(64), nullable=True, index=True)
    client_id = Column(String(36), ForeignKey('clients.id', ondelete='SET NULL'), nullable=True, index=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(36), nullable=True)
    ip_address = Column(String(45), nullable=True)
    previous_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)

    user = relationship("User", foreign_keys=[user_id], overlaps="audit_logs")

    __table_args__ = (
        Index('idx_audit_client_action', 'client_id', 'action'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_created_at', 'created_at'),
        {'extend_existing': True}
    )
