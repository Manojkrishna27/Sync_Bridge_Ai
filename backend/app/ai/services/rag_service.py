import uuid
from typing import Dict, Any, List
from app.models.copilot_model import KnowledgeSource, EmbeddingJob
from app.ai.rag.vector_store import vector_store
from app.core.extensions import db

DEFAULT_KNOWLEDGE_DOCS = [
    {
        "title": "SOAP to REST Conversion Rules Guide",
        "document_type": "CONNECTOR_DOC",
        "content": "To unwrap SOAP envelopes into REST JSON, locate GetCustomerRequest elements and extract CustomerId into REST id property."
    },
    {
        "title": "Enterprise Gateway Error Catalog",
        "document_type": "ERROR_CATALOG",
        "content": "ERR_VAL_001 indicates payload schema validation failure. Fix missing mandatory fields in raw payload."
    },
    {
        "title": "Circuit Breaker State Machine Guide",
        "document_type": "CONNECTOR_DOC",
        "content": "REST Connector transitions to OPEN state when consecutive failures reach 5. It transitions to HALF_OPEN after recovery timeout."
    }
]

class RAGService:
    """Enterprise RAG Service managing Knowledge Ingestion, Indexing, and Hybrid Vector Search."""

    def __init__(self):
        self.vector_store = vector_store

    def seed_initial_knowledge(self):
        for doc in DEFAULT_KNOWLEDGE_DOCS:
            existing = KnowledgeSource.query.filter_by(title=doc["title"]).first()
            if not existing:
                ks = KnowledgeSource(
                    id=str(uuid.uuid4()),
                    title=doc["title"],
                    document_type=doc["document_type"],
                    file_format="MARKDOWN",
                    raw_content=doc["content"],
                    status="INDEXED"
                )
                db.session.add(ks)
                self.vector_store.index_document(ks.id, doc["content"], {"title": doc["title"], "type": doc["document_type"]})
        db.session.commit()

    def add_knowledge_document(
        self,
        title: str,
        content: str,
        document_type: str = "HELP_GUIDE",
        file_format: str = "MARKDOWN",
        client_id: str = None,
        integration_id: str = None,
        tags: list = None
    ) -> KnowledgeSource:
        
        ks = KnowledgeSource(
            id=str(uuid.uuid4()),
            client_id=client_id,
            integration_id=integration_id,
            document_type=document_type,
            title=title,
            file_format=file_format,
            raw_content=content,
            tags=tags,
            status="INDEXED"
        )
        db.session.add(ks)
        db.session.commit()

        self.vector_store.index_document(
            ks.id,
            content,
            {"title": title, "type": document_type, "client_id": client_id, "integration_id": integration_id}
        )

        return ks

    def retrieve_context(self, query: str, client_id: str = None, top_k: int = 3) -> List[dict]:
        self.seed_initial_knowledge()
        return self.vector_store.search_hybrid(query, client_id=client_id, top_k=top_k)
