from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag import RAGEngine
import uvicorn
import logging
#import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI RAG POC API",
    description="Retrieval-Augmented Generation API deployed on AWS ECS",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    rag_engine = RAGEngine()
except Exception as e:
    logger.warning(f"RAG engine not initialized: {e}")
    rag_engine = None

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

class IngestRequest(BaseModel):
    documents: list[str]
    metadata: list[dict] = []

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    model: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "RAG POC", "version": "1.0.0"}

@app.get("/")
def root():
    return {
        "message": "AI RAG POC - Deployed on AWS ECS with Terraform & GitHub Actions CI/CD",
        "endpoints": {
            "health": "/health",
            "ingest": "POST /ingest",
            "query": "POST /query",
            "docs": "/docs"
        }
    }

@app.post("/ingest")
def ingest_documents(request: IngestRequest):
    if rag_engine is None:
        raise HTTPException(status_code=503, detail="RAG engine not initialized")
    try:
        count = rag_engine.ingest(request.documents, request.metadata)
        logger.info(f"Ingested {count} documents")
        return {"message": f"Successfully ingested {count} documents", "total_docs": count}
    except Exception as e:
        logger.error(f"Ingest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    if rag_engine is None:
        raise HTTPException(status_code=503, detail="RAG engine not initialized")
    try:
        result = rag_engine.query(request.question, request.top_k)
        logger.info(f"Query answered: {request.question[:50]}")
        return result
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def metrics():
    if rag_engine is None:
        return {
            "documents_indexed": 0,
            "queries_served": 0,
            "status": "rag_engine_not_initialized"
        }
    return {
        "documents_indexed": rag_engine.doc_count(),
        "queries_served": rag_engine.query_count,
        "status": "operational"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
