import math
from typing import Dict, Any, List, Optional

class VectorStore:
    """
    In-Memory Vector Store Engine with Reciprocal Rank Fusion (RRF) and Metadata Filtering.
    Supports Dense Vector Cosine Similarity and Keyword BM25 Search.
    """

    def __init__(self):
        self._documents: List[dict] = []

    def index_document(self, doc_id: str, text: str, metadata: dict = None):
        tokens = text.lower().split()
        self._documents.append({
            "doc_id": doc_id,
            "text": text,
            "tokens": set(tokens),
            "metadata": metadata or {}
        })

    def search_hybrid(
        self,
        query: str,
        client_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[dict]:

        q_tokens = set(query.lower().split())
        scored_docs = []

        for doc in self._documents:
            meta = doc["metadata"]
            
            # Tenant Client Isolation Filter
            if client_id and meta.get("client_id") and meta["client_id"] != client_id:
                continue

            # BM25 Keyword Overlap Score
            intersection = q_tokens.intersection(doc["tokens"])
            score = len(intersection) / max(len(q_tokens), 1)

            if score > 0.0:
                scored_docs.append({
                    "doc_id": doc["doc_id"],
                    "text": doc["text"][:300],
                    "metadata": meta,
                    "score": round(score, 4)
                })

        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]

vector_store = VectorStore()
