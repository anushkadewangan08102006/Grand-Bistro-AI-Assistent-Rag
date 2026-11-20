import os
import math
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
from typing import List, Dict, Any

class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
                import torch
                self._model = CrossEncoder(self.model_name, local_files_only=True)
                # Cast to float64 (double) to avoid Apple Silicon Accelerate float32 precision bugs
                if hasattr(self._model, "model"):
                    self._model.model.double()
            except Exception as e:
                print(f"Warning: Could not initialize CrossEncoder ({e}), using fallback ranker.")
                self._model = None
        return self._model

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        # If CrossEncoder is loaded, predict logits
        model = self.model
        if model is not None:
            try:
                pairs = [[query, c["text"]] for c in candidates]
                scores = model.predict(pairs)
                
                reranked = []
                for idx, score in enumerate(scores):
                    c = dict(candidates[idx])
                    val = float(score)
                    if math.isnan(val) or math.isinf(val):
                        val = float(c.get("rrf_score", 0.0))
                    c["rerank_score"] = round(val, 4)
                    reranked.append(c)

                reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
                for i, item in enumerate(reranked):
                    item["final_rank"] = i + 1
                return reranked[:top_k]
            except Exception as e:
                print(f"Reranking error ({e}), falling back to RRF order.")

        # Fallback to RRF rank
        reranked = [dict(c) for c in candidates]
        reranked.sort(key=lambda x: x.get("rrf_score", 0), reverse=True)
        for i, item in enumerate(reranked):
            item["rerank_score"] = float(item.get("rrf_score", 0.0))
            item["final_rank"] = i + 1
        return reranked[:top_k]
