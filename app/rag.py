import os
import pickle
from typing import List, Tuple, Optional
import faiss
from sentence_transformers import SentenceTransformer
import logging
import random

from app.models import Chunk, Citation, Answer
from app.hybrid_search import HybridSearcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGChat:
    def __init__(self, 
                 vector_store_path: str = "vector_store",
                 use_hybrid: bool = True):
        """
        Initialize RAG Chat system - NO API KEY REQUIRED!
        """
        self.vector_store_path = vector_store_path
        self.use_hybrid = use_hybrid
        
        # Load embedding model (for search only)
        logger.info("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load chunks and FAISS index
        self.load_vector_store()
        
        # Initialize hybrid searcher if needed
        if use_hybrid:
            logger.info("Initializing hybrid searcher...")
            self.hybrid_searcher = HybridSearcher(
                self.embedding_model,
                self.chunks,
                self.index
            )
        
    def load_vector_store(self):
        """Load chunks and FAISS index from disk"""
        try:
            with open(os.path.join(self.vector_store_path, "chunks.pkl"), "rb") as f:
                self.chunks = pickle.load(f)
            
            self.index = faiss.read_index(
                os.path.join(self.vector_store_path, "faiss.index")
            )
            
            with open(os.path.join(self.vector_store_path, "metadata.pkl"), "rb") as f:
                self.metadata = pickle.load(f)
            
            logger.info(f"✅ Loaded {len(self.chunks)} chunks")
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
            self.chunks = []
            self.index = None
    
    def retrieve_chunks(self, 
                       query: str, 
                       k: int = 5,
                       use_hybrid: bool = True) -> List[Tuple[Chunk, float]]:
        """Retrieve relevant chunks for query"""
        if not self.chunks or self.index is None:
            return []
            
        if use_hybrid and hasattr(self, 'hybrid_searcher'):
            return self.hybrid_searcher.hybrid_search(query, rerank_k=k)
        else:
            query_embedding = self.embedding_model.encode([query])
            faiss.normalize_L2(query_embedding)
            scores, indices = self.index.search(query_embedding, k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if 0 <= idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    score = float(scores[0][i])
                    results.append((chunk, score))
            
            return results
    
    def generate_answer(self, 
                       query: str, 
                       chunks: List[Tuple[Chunk, float]],
                       debug: bool = False) -> Answer:
        """Generate answer using PDF chunks - NO AI GENERATION"""
        
        # If no chunks found
        if not chunks or len(chunks) == 0:
            return Answer(
                answer="❌ This information is not available in the provided document(s).",
                citations=[],
                retrieved_chunks=[] if debug else None,
                search_type="hybrid" if self.use_hybrid else "vector"
            )
        
        # Prepare citations from top chunks
        citations = []
        retrieved = []
        
        for chunk, score in chunks[:3]:
            # Truncate text for display
            display_text = chunk.text[:300] + "..." if len(chunk.text) > 300 else chunk.text
            
            citation = Citation(
                document=chunk.document,
                page=chunk.page,
                chunk_id=chunk.id,
                text=display_text,
                relevance_score=score
            )
            citations.append(citation)
            
            retrieved.append({
                "text": display_text,
                "document": chunk.document,
                "page": chunk.page,
                "score": score
            })
        
        # Create answer from best chunk
        best_chunk = chunks[0][0]
        best_text = best_chunk.text
        
        # Simple answer formatting
        if len(best_text) > 500:
            answer_text = best_text[:500] + "..."
        else:
            answer_text = best_text
        
        # Add source info
        answer_text = f"📚 **Found in {best_chunk.document} (Page {best_chunk.page}):**\n\n{answer_text}"
        
        # Add additional sources if available
        if len(chunks) > 1:
            answer_text += f"\n\n📑 **Additional sources:** {', '.join(set(c.document for c, _ in chunks[1:3]))}"
        
        return Answer(
            answer=answer_text,
            citations=citations,
            retrieved_chunks=retrieved if debug else None,
            search_type="hybrid" if self.use_hybrid else "vector"
        )
    
    def ask(self, question: str, debug: bool = False, use_hybrid: bool = True) -> Answer:
        """Main method to ask questions"""
        try:
            # Retrieve relevant chunks
            chunks = self.retrieve_chunks(question, use_hybrid=use_hybrid)
            
            # Generate answer from chunks
            answer = self.generate_answer(question, chunks, debug)
            
            return answer
            
        except Exception as e:
            logger.error(f"Error in ask: {e}")
            return Answer(
                answer="❌ Error processing question. Please try again.",
                citations=[],
                retrieved_chunks=[] if debug else None,
                search_type="hybrid" if self.use_hybrid else "vector"
            )