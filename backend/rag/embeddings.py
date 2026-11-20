import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
from typing import List, Dict, Any
import chromadb

class EmbeddingService:
    def __init__(self, db_dir: str = "/Users/anushka/Desktop/genAI/data/chroma_db", collection_name: str = "culinary_manual"):
        self.db_dir = db_dir
        self.collection_name = collection_name
        os.makedirs(db_dir, exist_ok=True)
        
        self._model = None
        self.client = chromadb.PersistentClient(path=db_dir)

    @property
    def collection(self):
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
        return self._model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return embeddings.tolist()

    def index_chunks(self, chunks: List[Dict[str, Any]], clear_existing: bool = True):
        if not chunks:
            return

        col = self.collection

        ids = [c["chunk_id"] for c in chunks]
        texts = [c["text"] for c in chunks]
        metadatas = [{
            "page_num": c["page_num"],
            "chapter": c["chapter"],
            "module_num": str(c["module_num"]),
            "module_topic": c["module_topic"],
            "section_title": c.get("section_title", ""),
            "chunk_type": c.get("chunk_type", "operations")
        } for c in chunks]

        embeddings = self.embed_texts(texts)

        # Batch upsert into ChromaDB (upsert is atomic and does not destroy the collection)
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            col.upsert(
                ids=ids[i:i+batch_size],
                documents=texts[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
                embeddings=embeddings[i:i+batch_size]
            )

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        col = self.collection
        doc_count = col.count()
        if doc_count == 0:
            return []

        query_emb = self.embed_texts([query])[0]
        results = col.query(
            query_embeddings=[query_emb],
            n_results=min(top_k, doc_count),
            include=["documents", "metadatas", "distances"]
        )

        ranked = []
        if results and results["ids"] and results["ids"][0]:
            for rank_idx, doc_id in enumerate(results["ids"][0]):
                meta = results["metadatas"][0][rank_idx]
                doc = results["documents"][0][rank_idx]
                dist = results["distances"][0][rank_idx] if "distances" in results else 0.0
                similarity = 1.0 - float(dist)
                ranked.append({
                    "chunk_id": doc_id,
                    "text": doc,
                    "page_num": meta["page_num"],
                    "chapter": meta["chapter"],
                    "module_num": meta["module_num"],
                    "module_topic": meta["module_topic"],
                    "section_title": meta["section_title"],
                    "chunk_type": meta["chunk_type"],
                    "dense_score": round(similarity, 4),
                    "dense_rank": rank_idx + 1
                })
        return ranked
