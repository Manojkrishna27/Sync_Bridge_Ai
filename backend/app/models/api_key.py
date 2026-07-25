from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class APIKey(BaseModel):
    __tablename__ = 'api_keys'

    client_id = Column(String(36), ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True, index=True) # SHA-256 hash of the token secret
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False, default='Active', index=True) # Active, Revoked, Expired
    created_by = Column(String(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Relationships
    client = relationship("Client", back_populates="api_keys")

    __table_args__ = (
        Index('idx_apikey_client_status', 'client_id', 'status', 'deleted_at'),
    )
