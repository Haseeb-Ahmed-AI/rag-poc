import os
import logging
from typing import Optional
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate

load_dotenv()

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a helpful AI assistant. Use the following context to answer the question.
If you don't know the answer from the context, say so clearly.

Context:
{context}

Question: {question}

Answer:"""
)

class RAGEngine:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "dummy-key")
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        self.llm = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model_name=os.getenv("LLM_MODEL", "gpt-4o"),
            temperature=0.2
        )
        self.vectorstore: Optional[FAISS] = None
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
        self.query_count = 0
        # self._ingest_demo_docs()

    def _ingest_demo_docs(self):
        """Load demo documents on startup."""
        demo_docs = [
            "AWS ECS (Elastic Container Service) is a fully managed container orchestration service that makes it easy to deploy, manage, and scale containerized applications.",
            "Terraform is an Infrastructure as Code tool that allows you to define cloud infrastructure in configuration files that you can version, reuse, and share.",
            "GitHub Actions is a CI/CD platform that allows you to automate build, test, and deployment pipelines directly in your GitHub repository.",
            "RAG (Retrieval-Augmented Generation) combines a retrieval system with a generative AI model to produce accurate, grounded responses from your own data.",
            "AWS Auto Scaling automatically adjusts compute capacity based on defined conditions, ensuring optimal performance and cost efficiency.",
            "Amazon CloudWatch monitors AWS resources and applications in real time, providing metrics, logs, and alarms for infrastructure observability.",
            "AWS Application Load Balancer (ALB) automatically distributes incoming traffic across multiple targets such as ECS tasks, enabling high availability.",
            "FAISS (Facebook AI Similarity Search) is a library for efficient similarity search and clustering of dense vectors, commonly used in RAG pipelines.",
        ]
        self.ingest(demo_docs, [{"source": "demo"} for _ in demo_docs])
        logger.info("Demo documents loaded into vector store.")

    def ingest(self, documents: list[str], metadata: list[dict] = []) -> int:
        if not metadata or len(metadata) != len(documents):
            metadata = [{"source": f"doc_{i}"} for i in range(len(documents))]

        docs = [Document(page_content=text, metadata=meta)
                for text, meta in zip(documents, metadata)]
        chunks = self.splitter.split_documents(docs)

        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        else:
            self.vectorstore.add_documents(chunks)

        return len(chunks)

    def query(self, question: str, top_k: int = 3) -> dict:
        if self.vectorstore is None:
            raise ValueError("No documents indexed. Please ingest documents first.")

        retriever = self.vectorstore.as_retriever(search_kwargs={"k": top_k})
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": SYSTEM_PROMPT},
            return_source_documents=True
        )

        result = qa_chain({"query": question})
        self.query_count += 1

        sources = list({doc.metadata.get("source", "unknown")
                        for doc in result.get("source_documents", [])})

        return {
            "answer": result["result"],
            "sources": sources,
            "model": os.getenv("LLM_MODEL", "gpt-4o")
        }

    def doc_count(self) -> int:
        if self.vectorstore is None:
            return 0
        return self.vectorstore.index.ntotal
