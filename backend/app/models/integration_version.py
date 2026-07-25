from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Text, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class IntegrationVersion(BaseModel):
    __tablename__ = 'integration_versions'

    integration_id = Column(String(36), ForeignKey('integrations.id', ondelete='CASCADE'), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    snapshot = Column(JSON, nullable=False) # Full configuration state at this version
    change_notes = Column(Text, nullable=True)
    created_by = Column(String(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Relationships
    integration = relationship("Integration", back_populates="versions")

    __table_args__ = (
        Index('idx_version_integration_num', 'integration_id', 'version_number', unique=True),
    )
