from typing import List, Dict, Any

class HybridRetriever:
    def __init__(self, dense_service, bm25_service, rrf_k: int = 60):
        self.dense = dense_service
        self.bm25 = bm25_service
        self.rrf_k = rrf_k

    def search(self, query: str, top_k: int = 10, dense_candidates: int = 20, bm25_candidates: int = 20) -> List[Dict[str, Any]]:
        dense_results = self.dense.search(query, top_k=dense_candidates)
        bm25_results = self.bm25.search(query, top_k=bm25_candidates)

        combined: Dict[str, Dict[str, Any]] = {}

        # Add Dense results
        for rank_idx, doc in enumerate(dense_results):
            cid = doc["chunk_id"]
            dense_rank = rank_idx + 1
            rrf_score = 1.0 / (self.rrf_k + dense_rank)

            combined[cid] = {
                **doc,
                "dense_rank": dense_rank,
                "dense_score": doc.get("dense_score", 0.0),
                "bm25_rank": None,
                "bm25_score": 0.0,
                "rrf_score": rrf_score
            }

        # Add BM25 results
        for rank_idx, doc in enumerate(bm25_results):
            cid = doc["chunk_id"]
            bm25_rank = rank_idx + 1
            additional_rrf = 1.0 / (self.rrf_k + bm25_rank)

            if cid in combined:
                combined[cid]["bm25_rank"] = bm25_rank
                combined[cid]["bm25_score"] = doc.get("bm25_score", 0.0)
                combined[cid]["rrf_score"] += additional_rrf
            else:
                combined[cid] = {
                    **doc,
                    "dense_rank": None,
                    "dense_score": 0.0,
                    "bm25_rank": bm25_rank,
                    "bm25_score": doc.get("bm25_score", 0.0),
                    "rrf_score": additional_rrf
                }

        # Sort by RRF score descending
        fused = list(combined.values())
        fused.sort(key=lambda x: x["rrf_score"], reverse=True)

        for i, item in enumerate(fused):
            item["rrf_rank"] = i + 1
            item["rrf_score"] = round(item["rrf_score"], 6)

        return fused[:top_k]
