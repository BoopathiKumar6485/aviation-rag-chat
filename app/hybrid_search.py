import numpy as np
from typing import List, Tuple, Dict, Any
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss
from app.models import Chunk
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridSearcher:
    def __init__(self, 
                 embedding_model: SentenceTransformer,
                 chunks: List[Chunk],
                 faiss_index: faiss.Index):
        """
        Initialize hybrid search with BM25 + Vector + Reranker
        """
        self.model = embedding_model
        self.chunks = chunks
        self.index = faiss_index
        
        # Prepare BM25 (keyword search)
        logger.info("Initializing BM25 index...")
        self.tokenized_chunks = [chunk.text.split() for chunk in chunks]
        self.bm25 = BM25Okapi(self.tokenized_chunks)
        
        # Load cross-encoder for reranking
        logger.info("Loading cross-encoder for reranking...")
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
    def vector_search(self, query: str, k: int = 10) -> List[Tuple[Chunk, float]]:
        """
        Vector similarity search using FAISS
        """
        # Encode query
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search FAISS index
        scores, indices = self.index.search(query_embedding, k)
        
        # Return chunks with scores
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # Valid index
                chunk = self.chunks[idx]
                score = float(scores[0][i])
                results.append((chunk, score))
        
        return results
    
    def bm25_search(self, query: str, k: int = 10) -> List[Tuple[Chunk, float]]:
        """
        Keyword search using BM25
        """
        # Tokenize query
        tokenized_query = query.split()
        
        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top k indices
        top_indices = np.argsort(scores)[-k:][::-1]
        
        # Return chunks with scores
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include if score > 0
                chunk = self.chunks[idx]
                score = float(scores[idx])
                results.append((chunk, score))
        
        return results
    
    def hybrid_search(self, 
                     query: str, 
                     vector_k: int = 15,
                     bm25_k: int = 15,
                     rerank_k: int = 5) -> List[Tuple[Chunk, float]]:
        """
        Hybrid search: Vector + BM25 + Reranker
        Strategy:
        1. Get candidates from vector search (semantic)
        2. Get candidates from BM25 search (keyword)
        3. Combine and deduplicate
        4. Rerank with cross-encoder
        """
        logger.info(f"Performing hybrid search for: {query}")
        
        # Step 1 & 2: Get candidates from both methods
        vector_results = self.vector_search(query, k=vector_k)
        bm25_results = self.bm25_search(query, k=bm25_k)
        
        # Step 3: Combine and deduplicate
        chunk_scores = {}
        
        # Add vector results (weight: 0.5)
        for chunk, score in vector_results:
            # Normalize vector score to 0-1 range
            norm_score = (score + 1) / 2  # FAISS IP score ranges from -1 to 1
            chunk_scores[chunk.id] = {
                "chunk": chunk,
                "vector_score": norm_score,
                "bm25_score": 0,
                "combined_score": norm_score * 0.5
            }
        
        # Add BM25 results (weight: 0.5)
        for chunk, score in bm25_results:
            # Normalize BM25 score (simple min-max)
            if score > 0:
                if chunk.id in chunk_scores:
                    chunk_scores[chunk.id]["bm25_score"] = score
                    chunk_scores[chunk.id]["combined_score"] = (
                        chunk_scores[chunk.id]["vector_score"] * 0.5 + 
                        score * 0.5
                    )
                else:
                    chunk_scores[chunk.id] = {
                        "chunk": chunk,
                        "vector_score": 0,
                        "bm25_score": score,
                        "combined_score": score * 0.5
                    }
        
        # Convert to list and sort by combined score
        candidates = list(chunk_scores.values())
        candidates.sort(key=lambda x: x["combined_score"], reverse=True)
        
        # Step 4: Rerank top candidates with cross-encoder
        top_candidates = candidates[:rerank_k * 2]  # Take more for reranking
        
        if top_candidates:
            # Prepare pairs for cross-encoder
            pairs = [(query, c["chunk"].text) for c in top_candidates]
            
            # Get reranking scores
            rerank_scores = self.reranker.predict(pairs)
            
            # Update scores
            for i, (candidate, rerank_score) in enumerate(zip(top_candidates, rerank_scores)):
                candidate["rerank_score"] = float(rerank_score)
                candidate["final_score"] = (
                    candidate["combined_score"] * 0.3 + 
                    float(rerank_score) * 0.7
                )
            
            # Sort by final score
            top_candidates.sort(key=lambda x: x["final_score"], reverse=True)
            
            # Return top k
            results = [(c["chunk"], c["final_score"]) 
                      for c in top_candidates[:rerank_k]]
        else:
            results = []
        
        # Log search metrics
        logger.info(f"Vector results: {len(vector_results)}, "
                   f"BM25 results: {len(bm25_results)}, "
                   f"Final results: {len(results)}")
        
        return results
    
    def search_with_explanation(self, query: str) -> Dict[str, Any]:
        """
        Search with detailed explanation (for debugging)
        """
        # Get results from each method
        vector_results = self.vector_search(query, k=5)
        bm25_results = self.bm25_search(query, k=5)
        hybrid_results = self.hybrid_search(query)
        
        return {
            "query": query,
            "vector_results": [
                {
                    "text": chunk.text[:200] + "...",
                    "score": score,
                    "document": chunk.document,
                    "page": chunk.page
                }
                for chunk, score in vector_results
            ],
            "bm25_results": [
                {
                    "text": chunk.text[:200] + "...",
                    "score": score,
                    "document": chunk.document,
                    "page": chunk.page
                }
                for chunk, score in bm25_results
            ],
            "hybrid_results": [
                {
                    "text": chunk.text[:200] + "...",
                    "score": score,
                    "document": chunk.document,
                    "page": chunk.page
                }
                for chunk, score in hybrid_results
            ]
        }