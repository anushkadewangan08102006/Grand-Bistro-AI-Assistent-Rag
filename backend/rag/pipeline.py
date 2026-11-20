import os
import time
from typing import List, Dict, Any, Optional
from backend.rag.ingestion import PDFIngestionService
from backend.rag.chunking import DocumentChunker
from backend.rag.embeddings import EmbeddingService
from backend.rag.bm25_retriever import BM25Retriever
from backend.rag.hybrid_retriever import HybridRetriever
from backend.rag.reranker import CrossEncoderReranker
from backend.rag.external_search import ExternalSearchService
from backend.rag.generator import LLMAnswerGenerator

class CulinaryRAGPipeline:
    def __init__(self, pdf_path: str = "/Users/anushka/Desktop/genAI/grand_bistro_culinary_recipe_manual_50p.pdf"):
        self.pdf_path = pdf_path
        self.ingestion = PDFIngestionService(pdf_path)
        self.chunker = DocumentChunker()
        self.embeddings = EmbeddingService()
        self.bm25 = BM25Retriever()
        self.hybrid = HybridRetriever(self.embeddings, self.bm25, rrf_k=60)
        self.reranker = CrossEncoderReranker()
        self.external_search = ExternalSearchService()
        self.generator = LLMAnswerGenerator()

        self.pages_data: List[Dict[str, Any]] = []
        self.chunks: List[Dict[str, Any]] = []
        self.is_indexed: bool = False
        self.last_indexed_time: Optional[float] = None

    def initialize_and_index(self, force: bool = False):
        """
        Extract text from all 50 pages, chunk, embed, and index for hybrid retrieval.
        """
        if self.is_indexed and not force:
            return

        print(f"[RAG Pipeline] Ingesting PDF from: {self.pdf_path}")
        self.pages_data = self.ingestion.extract_pages(self.pdf_path)
        print(f"[RAG Pipeline] Extracted {len(self.pages_data)} pages.")

        self.chunks = self.chunker.chunk_pages(self.pages_data)
        print(f"[RAG Pipeline] Generated {len(self.chunks)} structured chunks.")

        print("[RAG Pipeline] Indexing chunks in BM25...")
        self.bm25.index_chunks(self.chunks)

        print("[RAG Pipeline] Generating dense embeddings & indexing in ChromaDB...")
        self.embeddings.index_chunks(self.chunks, clear_existing=True)

        self.is_indexed = True
        self.last_indexed_time = time.time()
        print("[RAG Pipeline] Pipeline initialization complete.")

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        dense_k: int = 15,
        bm25_k: int = 15,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Full RAG retrieval and answer pipeline:
        1. Classify intent: Document RAG vs External Knowledge
        2. If external: run external web search & generate external response
        3. If document:
           - Dense retrieval
           - BM25 retrieval
           - RRF Hybrid fusion
           - Cross-Encoder re-ranking
           - LLM Answer generation with exact page citations
        """
        start_time = time.time()
        if not self.is_indexed:
            self.initialize_and_index()

        is_external = self.external_search.is_external_query(query_text)

        if is_external:
            print(f"[Pipeline] Query detected as external knowledge: '{query_text}'")
            external_results = self.external_search.search(query_text, max_results=4)
            generation_result = self.generator.generate_answer(
                query=query_text,
                retrieved_chunks=[],
                external_results=external_results,
                is_external=True,
                conversation_history=conversation_history
            )
            elapsed = round((time.time() - start_time) * 1000, 2)
            return {
                "query": query_text,
                "is_external": True,
                "answer": generation_result["answer"],
                "source_type": "external",
                "citations": generation_result["citations"],
                "confidence": generation_result.get("confidence", "verified_external"),
                "retrieval_stats": {
                    "latency_ms": elapsed,
                    "retrieval_type": "external_web_search",
                    "sources_found": len(external_results)
                },
                "retrieved_chunks": []
            }

        # Step 4: Hybrid Retrieval (BM25 + Dense + RRF)
        try:
            fused_candidates = self.hybrid.search(
                query=query_text,
                top_k=top_k * 2,
                dense_candidates=dense_k,
                bm25_candidates=bm25_k
            )
        except Exception as e:
            print(f"[RAG Pipeline] Hybrid retrieval warning: {e}, falling back to keyword BM25.")
            fused_candidates = self.bm25.search(query=query_text, top_k=top_k * 2)

        # Step 5: Cross-Encoder Re-ranking
        try:
            reranked_chunks = self.reranker.rerank(
                query=query_text,
                candidates=fused_candidates,
                top_k=top_k
            )
        except Exception as e:
            print(f"[RAG Pipeline] Reranking warning: {e}, using fused order.")
            reranked_chunks = fused_candidates[:top_k]

        # Step 6: LLM Answer Generation
        generation_result = self.generator.generate_answer(
            query=query_text,
            retrieved_chunks=reranked_chunks,
            is_external=False,
            conversation_history=conversation_history
        )

        elapsed = round((time.time() - start_time) * 1000, 2)

        return {
            "query": query_text,
            "is_external": False,
            "answer": generation_result["answer"],
            "source_type": "document",
            "citations": generation_result["citations"],
            "confidence": generation_result.get("confidence", "high"),
            "retrieval_stats": {
                "latency_ms": elapsed,
                "retrieval_type": "hybrid_bm25_dense_rrf_cross_encoder",
                "dense_candidates": dense_k,
                "bm25_candidates": bm25_k,
                "reranked_count": len(reranked_chunks)
            },
            "retrieved_chunks": reranked_chunks
        }
