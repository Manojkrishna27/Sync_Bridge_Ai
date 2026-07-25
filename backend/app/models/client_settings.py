from sqlalchemy import Column, String, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class ClientSettings(BaseModel):
    __tablename__ = 'client_settings'

    client_id = Column(String(36), ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    timezone = Column(String(100), nullable=False, default='UTC')
    default_environment = Column(String(50), nullable=False, default='Development')
    retry_policy = Column(JSON, nullable=False, default=lambda: {"max_retries": 3, "backoff_factor": 2})
    notification_preferences = Column(JSON, nullable=False, default=lambda: {"email": True, "slack_webhook": None})
    ai_preferences = Column(JSON, nullable=False, default=lambda: {"auto_mapping": True, "error_analysis": True})
    webhook_configuration = Column(JSON, nullable=True, default=dict)

    # Relationships
    client = relationship("Client", back_populates="settings")

    __table_args__ = (
        Index('idx_client_settings_client_id', 'client_id'),
    )
