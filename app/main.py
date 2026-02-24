from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from typing import Optional

from app.models import Question, Answer, IngestResponse, HealthResponse
from app.ingest import PDFIngestor
from app.rag import RAGChat

app = FastAPI(title="Aviation RAG Chat API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
ingestor = None
rag_chat = None

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global ingestor, rag_chat
    
    # Create data directory if not exists
    os.makedirs("data", exist_ok=True)
    os.makedirs("vector_store", exist_ok=True)
    
    # Initialize ingestor
    ingestor = PDFIngestor()
    
    # Try to load existing vector store
    try:
        rag_chat = RAGChat(vector_store_path="vector_store")
        print("Loaded existing vector store")
    except:
        print("No existing vector store found. Please ingest documents first.")
        rag_chat = None

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        vector_store_loaded=rag_chat is not None,
        chunks_count=len(rag_chat.chunks) if rag_chat else 0,
        model_loaded=True
    )

@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents():
    """Ingest PDF documents from data folder"""
    global rag_chat
    
    try:
        # Run ingestion
        result = ingestor.ingest_pdfs(pdf_folder="data")
        
        # Reinitialize RAG chat with new vector store
        rag_chat = RAGChat(vector_store_path="vector_store")
        
        return IngestResponse(
            status="success",
            chunks_created=result["chunks_created"],
            documents_processed=result["documents_processed"],
            vector_store_size=len(rag_chat.chunks) if rag_chat else 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file to data folder"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_path = os.path.join("data", file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename, "status": "uploaded"}

@app.post("/ask", response_model=Answer)
async def ask_question(question: Question):
    """Ask a question to the RAG system"""
    global rag_chat
    
    if rag_chat is None:
        raise HTTPException(
            status_code=400, 
            detail="No documents ingested yet. Please ingest documents first."
        )
    
    try:
        answer = rag_chat.ask(
            question=question.text,
            debug=question.debug,
            use_hybrid=question.use_hybrid
        )
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/debug")
async def debug_search(query: str):
    """Debug endpoint to see search results"""
    if rag_chat is None or not hasattr(rag_chat, 'hybrid_searcher'):
        raise HTTPException(status_code=400, detail="Hybrid searcher not initialized")
    
    try:
        explanation = rag_chat.hybrid_searcher.search_with_explanation(query)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)