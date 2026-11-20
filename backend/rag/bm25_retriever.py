import re
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi

class BM25Retriever:
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.bm25: BM25Okapi = None

    def tokenize(self, text: str) -> List[str]:
        # Clean alphanumeric tokens, lowercase
        tokens = re.findall(r'\b[a-zA-Z0-9_\-\.]+\b', text.lower())
        return tokens

    def index_chunks(self, chunks: List[Dict[str, Any]]):
        self.chunks = chunks
        if not chunks:
            self.bm25 = None
            return

        corpus = [self.tokenize(c["text"]) for c in chunks]
        self.bm25 = BM25Okapi(corpus)

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        if not self.bm25 or not self.chunks:
            return []

        tokenized_query = self.tokenize(query)
        if not tokenized_query:
            return []

        doc_scores = self.bm25.get_scores(tokenized_query)
        # Pair with indices
        scored_pairs = list(enumerate(doc_scores))
        scored_pairs.sort(key=lambda x: x[1], reverse=True)

        top_results = []
        for rank_idx, (idx, score) in enumerate(scored_pairs[:top_k]):
            if score <= 0:
                continue
            chunk = dict(self.chunks[idx])
            chunk["bm25_score"] = round(float(score), 4)
            chunk["bm25_rank"] = rank_idx + 1
            top_results.append(chunk)

        return top_results
