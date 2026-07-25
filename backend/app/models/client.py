from sqlalchemy import Column, String, Text, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class Client(BaseModel):
    __tablename__ = 'clients'

    name = Column(String(255), nullable=False, index=True)
    industry = Column(String(100), nullable=True, index=True)
    contact_person = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    country = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default='Active', index=True)  # Active, Inactive, Suspended
    subscription_plan = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True, default=list) # e.g. ["Finance", "Critical"]
    notes = Column(Text, nullable=True)
    created_by = Column(String(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Relationships
    settings = relationship("ClientSettings", uselist=False, back_populates="client", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="client", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="client", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_client_status_deleted', 'status', 'deleted_at'),
        Index('idx_client_name_search', 'name', 'deleted_at'),
    )
