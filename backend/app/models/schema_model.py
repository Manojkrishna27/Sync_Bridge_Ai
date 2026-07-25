from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class Schema(BaseModel):
    __tablename__ = 'schemas'

    client_id = Column(String(36), ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    format = Column(String(50), nullable=False) # JSON, XML, SOAP, CSV, OPENAPI, SWAGGER, XSD
    description = Column(Text, nullable=True)

    versions = relationship("SchemaVersion", back_populates="schema", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_schema_client_format', 'client_id', 'format'),
        {'extend_existing': True}
    )

class SchemaVersion(BaseModel):
    __tablename__ = 'schema_versions'

    schema_id = Column(String(36), ForeignKey('schemas.id', ondelete='CASCADE'), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, default=1)
    raw_schema = Column(Text, nullable=False)
    parsed_tree = Column(JSON, nullable=False)
    change_description = Column(String(255), nullable=True)

    schema = relationship("Schema", back_populates="versions")

    __table_args__ = (
        Index('idx_schema_ver_unique', 'schema_id', 'version_number', unique=True),
        {'extend_existing': True}
    )

class Mapping(BaseModel):
    __tablename__ = 'mappings'

    client_id = Column(String(36), ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    integration_id = Column(String(36), ForeignKey('integrations.id', ondelete='SET NULL'), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    source_schema_id = Column(String(36), ForeignKey('schemas.id', ondelete='SET NULL'), nullable=True)
    target_schema_id = Column(String(36), ForeignKey('schemas.id', ondelete='SET NULL'), nullable=True)
    version = Column(Integer, nullable=False, default=1)

    rules = relationship("MappingRule", back_populates="mapping", cascade="all, delete-orphan")
    versions = relationship("MappingVersion", back_populates="mapping", cascade="all, delete-orphan")
    ai_suggestions = relationship("AISuggestion", back_populates="mapping", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_map_client_integration', 'client_id', 'integration_id'),
        {'extend_existing': True}
    )

class MappingRule(BaseModel):
    __tablename__ = 'mapping_rules'

    mapping_id = Column(String(36), ForeignKey('mappings.id', ondelete='CASCADE'), nullable=False, index=True)
    source_path = Column(String(500), nullable=False)
    target_path = Column(String(500), nullable=False)
    rule_type = Column(String(50), nullable=False, default='STATIC') # STATIC, LOOKUP, CONDITIONAL, TRANSFORM
    strategy_used = Column(String(50), nullable=False, default='MANUAL') # SAVED_MAPPING, TEMPLATE, HEURISTIC, AI_MATCH, MANUAL
    config = Column(JSON, nullable=True)

    mapping = relationship("Mapping", back_populates="rules")

    __table_args__ = (
        Index('idx_rule_map_target', 'mapping_id', 'target_path'),
        {'extend_existing': True}
    )

class MappingVersion(BaseModel):
    __tablename__ = 'mapping_versions'

    mapping_id = Column(String(36), ForeignKey('mappings.id', ondelete='CASCADE'), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    rules_snapshot = Column(JSON, nullable=False)
    created_by = Column(String(255), nullable=True)
    change_description = Column(String(255), nullable=True)

    mapping = relationship("Mapping", back_populates="versions")

    __table_args__ = (
        Index('idx_map_ver_unique', 'mapping_id', 'version_number', unique=True),
        {'extend_existing': True}
    )

class AISuggestion(BaseModel):
    __tablename__ = 'ai_suggestions'

    mapping_id = Column(String(36), ForeignKey('mappings.id', ondelete='CASCADE'), nullable=False, index=True)
    source_field = Column(String(500), nullable=False)
    target_field = Column(String(500), nullable=False)
    confidence_score = Column(Float, nullable=False, default=0.0)
    reason = Column(Text, nullable=True)
    suggested_rule = Column(JSON, nullable=True)
    status = Column(String(50), nullable=False, default='PENDING') # ACCEPTED, REJECTED, MODIFIED, IGNORED

    mapping = relationship("Mapping", back_populates="ai_suggestions")

    __table_args__ = (
        Index('idx_ai_sug_mapping_status', 'mapping_id', 'status'),
        {'extend_existing': True}
    )

class TransformationTemplate(BaseModel):
    __tablename__ = 'transformation_templates'

    name = Column(String(255), nullable=False, unique=True)
    category = Column(String(100), nullable=False, default='General') # SAP -> Salesforce, Oracle -> REST
    description = Column(Text, nullable=True)
    rules = Column(JSON, nullable=False)

    __table_args__ = ({'extend_existing': True},)
