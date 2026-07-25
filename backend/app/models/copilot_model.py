from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class Conversation(BaseModel):
    __tablename__ = 'conversations'

    client_id = Column(String(36), ForeignKey('clients.id', ondelete='CASCADE'), nullable=True, index=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="New Integration Chat")
    is_pinned = Column(Boolean, nullable=False, default=False)
    is_archived = Column(Boolean, nullable=False, default=False)
    tags = Column(JSON, nullable=True) # e.g. ["SOAP", "Mapping"]
    category = Column(String(50), nullable=True, default="GENERAL") # MAPPING, TROUBLESHOOTING, PERFORMANCE

    messages = relationship("Message", backref="conversation", cascade="all, delete-orphan", order_by="Message.created_at")

    __table_args__ = (
        Index('idx_conv_user_pinned', 'user_id', 'is_pinned'),
        {'extend_existing': True}
    )

class Message(BaseModel):
    __tablename__ = 'messages'

    conversation_id = Column(String(36), ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True)
    role = Column(String(20), nullable=False) # user, assistant, system, tool
    content = Column(Text, nullable=False)
    
    # Explainability Metadata
    sources = Column(JSON, nullable=True) # Source document references
    retrieved_chunks = Column(JSON, nullable=True)
    agents_executed = Column(JSON, nullable=True)
    tool_calls = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True, default=0.95)
    total_time_ms = Column(Float, nullable=True, default=0.0)
    llm_time_ms = Column(Float, nullable=True, default=0.0)
    retrieval_time_ms = Column(Float, nullable=True, default=0.0)
    token_usage = Column(JSON, nullable=True) # {"prompt_tokens": 150, "completion_tokens": 300}
    provider = Column(String(50), nullable=True, default="MockProvider")
    model = Column(String(50), nullable=True, default="gpt-3.5-turbo")
    reasoning_summary = Column(Text, nullable=True)

    __table_args__ = ({'extend_existing': True},)

class PromptTemplate(BaseModel):
    __tablename__ = 'prompt_templates'

    category = Column(String(50), nullable=False, index=True) # SYSTEM, MAPPING, TROUBLESHOOTING, PERFORMANCE
    name = Column(String(100), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    template_text = Column(Text, nullable=False)

    __table_args__ = (
        Index('idx_prompt_cat_ver', 'category', 'version'),
        {'extend_existing': True}
    )

class KnowledgeSource(BaseModel):
    __tablename__ = 'knowledge_sources'

    client_id = Column(String(36), ForeignKey('clients.id', ondelete='CASCADE'), nullable=True, index=True)
    integration_id = Column(String(36), ForeignKey('integrations.id', ondelete='CASCADE'), nullable=True, index=True)
    document_type = Column(String(50), nullable=False) # OPENAPI, CONNECTOR_DOC, ERROR_CATALOG, HELP_GUIDE
    title = Column(String(255), nullable=False)
    file_format = Column(String(20), nullable=False, default="MARKDOWN") # PDF, MARKDOWN, JSON, XML, CSV
    raw_content = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    tags = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, default="INDEXED") # INDEXED, PENDING, ERROR

    __table_args__ = ({'extend_existing': True},)

class EmbeddingJob(BaseModel):
    __tablename__ = 'embedding_jobs'

    source_id = Column(String(36), ForeignKey('knowledge_sources.id', ondelete='CASCADE'), nullable=False)
    status = Column(String(20), nullable=False, default="PENDING") # PENDING, RUNNING, COMPLETED, FAILED
    chunk_count = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)

    __table_args__ = ({'extend_existing': True},)

class AIUsage(BaseModel):
    __tablename__ = 'ai_usage'

    user_id = Column(String(36), nullable=True, index=True)
    client_id = Column(String(36), nullable=True, index=True)
    provider = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    prompt_tokens = Column(Integer, nullable=False, default=0)
    completion_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    cost_estimate = Column(Float, nullable=False, default=0.0)
    latency_ms = Column(Float, nullable=False, default=0.0)

    __table_args__ = ({'extend_existing': True},)
