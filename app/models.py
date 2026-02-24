from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from enum import Enum

# ============================================
# Request Models
# ============================================

class Question(BaseModel):
    """Question from user"""
    text: str = Field(..., description="User question", example="What are flight levels referenced to?")
    debug: bool = Field(False, description="Show retrieved chunks in response", example=True)
    use_hybrid: bool = Field(True, description="Use hybrid search (BM25 + Vector + Reranker)", example=True)


# ============================================
# Response Models
# ============================================

class Citation(BaseModel):
    """Citation information for answer"""
    document: str = Field(..., description="Source document name", example="10-General-Navigation-2014.pdf")
    page: Optional[int] = Field(None, description="Page number in document", example=42)
    chunk_id: str = Field(..., description="Unique chunk identifier", example="chunk_1_abc123")
    text: str = Field(..., description="Relevant text snippet", example="Flight levels are referenced to standard pressure datum...")
    relevance_score: float = Field(..., description="Relevance score (0-1)", example=0.89)


class Answer(BaseModel):
    """Answer from RAG system"""
    answer: str = Field(..., description="Generated answer with citations", example="Flight levels are referenced to standard pressure datum (1013.25 hPa)...")
    citations: List[Citation] = Field(default_factory=list, description="List of citations supporting the answer")
    retrieved_chunks: Optional[List[Dict[str, Any]]] = Field(None, description="Raw retrieved chunks (only in debug mode)")
    search_type: str = Field("hybrid", description="Search method used (vector/hybrid)", example="hybrid")


# ============================================
# Data Models
# ============================================

class Chunk(BaseModel):
    """Document chunk model"""
    id: str = Field(..., description="Unique chunk identifier", example="chunk_1_abc123")
    text: str = Field(..., description="Chunk text content", example="Flight levels are referenced to...")
    document: str = Field(..., description="Source document name", example="10-General-Navigation-2014.pdf")
    page: int = Field(..., description="Page number", example=1)
    embedding: Optional[List[float]] = Field(None, description="Vector embedding (optional, for storage)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# ============================================
# API Response Models
# ============================================

class IngestResponse(BaseModel):
    """Response after document ingestion"""
    status: str = Field(..., description="Status of ingestion", example="success")
    chunks_created: int = Field(..., description="Number of chunks created", example=11051)
    documents_processed: List[str] = Field(..., description="List of processed documents", 
                                           example=["10-General-Navigation-2014.pdf", "Meteorology full book.pdf"])
    vector_store_size: int = Field(..., description="Total chunks in vector store", example=11051)


class HealthResponse(BaseModel):
    """Health check response"""
    model_config = ConfigDict(protected_namespaces=())  # Fix warning
    
    status: str = Field(..., description="Health status", example="healthy")
    vector_store_loaded: bool = Field(..., description="Whether vector store is loaded", example=True)
    chunks_count: int = Field(..., description="Number of chunks in vector store", example=11051)
    model_loaded: bool = Field(..., description="Whether embedding model is loaded", example=True)


# ============================================
# Error Models
# ============================================

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error details", example="Document not found")
    status_code: int = Field(..., description="HTTP status code", example=404)


# ============================================
# Enums (if needed)
# ============================================

class SearchType(str, Enum):
    """Search type enum"""
    VECTOR = "vector"
    HYBRID = "hybrid"
    BM25 = "bm25"


class DocumentType(str, Enum):
    """Document type enum"""
    PDF = "pdf"
    TEXT = "txt"
    UNKNOWN = "unknown"


# ============================================
# Usage Examples (commented out)
# ============================================

"""
# Example Question:
{
    "text": "What are flight levels referenced to?",
    "debug": true,
    "use_hybrid": true
}

# Example Answer:
{
    "answer": "📚 Found in 10-General-Navigation-2014.pdf (Page 1):\n\nFlight levels are referenced to standard pressure datum (1013.25 hPa)...",
    "citations": [
        {
            "document": "10-General-Navigation-2014.pdf",
            "page": 1,
            "chunk_id": "chunk_1_abc123",
            "text": "Flight levels are referenced to standard pressure datum...",
            "relevance_score": 0.89
        }
    ],
    "search_type": "hybrid"
}
"""