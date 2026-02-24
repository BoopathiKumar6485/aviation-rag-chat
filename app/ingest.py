import os
import pickle
import hashlib
from typing import List, Dict, Any
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from app.models import Chunk
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFIngestor:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the PDF ingestor with embedding model"""
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        self.chunks: List[Chunk] = []
        self.index = None
        
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF with page numbers"""
        logger.info(f"Extracting text from: {pdf_path}")
        pages = []
        reader = PdfReader(pdf_path)
        
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text.strip():  # Only add non-empty pages
                pages.append({
                    "text": text,
                    "page": page_num,
                    "document": os.path.basename(pdf_path)
                })
        
        logger.info(f"Extracted {len(pages)} pages")
        return pages
    
    def chunk_text(self, pages: List[Dict[str, Any]], 
                   chunk_size: int = 500, 
                   overlap: int = 50) -> List[Chunk]:
        """
        Chunk text with strategy explanation:
        - chunk_size=500 characters: Optimal for semantic search, not too short/long
        - overlap=50 characters: Maintain context between chunks
        - Rationale: Aviation documents have technical terms that need context,
          but chunks shouldn't be too large to maintain specificity
        """
        logger.info(f"Chunking text with size={chunk_size}, overlap={overlap}")
        chunks = []
        chunk_id = 0
        
        for page in pages:
            text = page["text"]
            document = page["document"]
            page_num = page["page"]
            
            # Split into chunks with overlap
            start = 0
            text_length = len(text)
            
            while start < text_length:
                end = min(start + chunk_size, text_length)
                
                # Get chunk text
                chunk_text = text[start:end]
                
                # Create chunk ID (hash for uniqueness)
                chunk_hash = hashlib.md5(
                    f"{document}_{page_num}_{start}_{end}".encode()
                ).hexdigest()[:8]
                
                chunk = Chunk(
                    id=f"chunk_{chunk_id}_{chunk_hash}",
                    text=chunk_text,
                    document=document,
                    page=page_num,
                    metadata={
                        "start_char": start,
                        "end_char": end,
                        "chunk_size": len(chunk_text)
                    }
                )
                
                chunks.append(chunk)
                
                # Move start with overlap
                start += (chunk_size - overlap)
                chunk_id += 1
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def create_embeddings(self, chunks: List[Chunk]) -> np.ndarray:
        """Create embeddings for chunks"""
        logger.info("Creating embeddings for chunks")
        texts = [chunk.text for chunk in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings
    
    def build_faiss_index(self, embeddings: np.ndarray):
        """Build FAISS index for vector search"""
        logger.info("Building FAISS index")
        dimension = embeddings.shape[1]
        
        # Using IndexFlatIP for inner product (cosine similarity with normalized vectors)
        self.index = faiss.IndexFlatIP(dimension)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        logger.info(f"Added {self.index.ntotal} vectors to index")
    
    def save(self, vector_store_path: str = "vector_store"):
        """Save chunks and index to disk"""
        os.makedirs(vector_store_path, exist_ok=True)
        
        # Save chunks
        with open(os.path.join(vector_store_path, "chunks.pkl"), "wb") as f:
            pickle.dump(self.chunks, f)
        
        # Save FAISS index
        faiss.write_index(self.index, 
                         os.path.join(vector_store_path, "faiss.index"))
        
        # Save metadata
        metadata = {
            "chunks_count": len(self.chunks),
            "embedding_dim": self.embedding_dim,
            "model_name": self.model.get_sentence_embedding_dimension()
        }
        with open(os.path.join(vector_store_path, "metadata.pkl"), "wb") as f:
            pickle.dump(metadata, f)
        
        logger.info(f"Saved vector store to {vector_store_path}")
    
    def load(self, vector_store_path: str = "vector_store"):
        """Load chunks and index from disk"""
        # Load chunks
        with open(os.path.join(vector_store_path, "chunks.pkl"), "rb") as f:
            self.chunks = pickle.load(f)
        
        # Load FAISS index
        self.index = faiss.read_index(
            os.path.join(vector_store_path, "faiss.index")
        )
        
        logger.info(f"Loaded {len(self.chunks)} chunks from {vector_store_path}")
    
    def ingest_pdfs(self, pdf_folder: str = "data"):
        """Main ingestion pipeline"""
        all_chunks = []
        
        # Process all PDFs in folder
        for pdf_file in os.listdir(pdf_folder):
            if pdf_file.endswith(".pdf"):
                pdf_path = os.path.join(pdf_folder, pdf_file)
                
                # Extract text
                pages = self.extract_text_from_pdf(pdf_path)
                
                # Chunk text
                chunks = self.chunk_text(pages)
                all_chunks.extend(chunks)
        
        self.chunks = all_chunks
        
        # Create embeddings
        embeddings = self.create_embeddings(self.chunks)
        
        # Build FAISS index
        self.build_faiss_index(embeddings)
        
        # Save to disk
        self.save()
        
        return {
            "chunks_created": len(self.chunks),
            "documents_processed": list(set(c.document for c in self.chunks))
        }

if __name__ == "__main__":
    # Test ingestion
    ingestor = PDFIngestor()
    result = ingestor.ingest_pdfs()
    print(f"Ingestion complete: {result}")