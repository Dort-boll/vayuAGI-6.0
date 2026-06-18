"""Memory Fabric — Semantic Cache using keyword overlap."""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path
from typing import Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from ..config import CONFIG
from ..logger import get_logger

log = get_logger("memory")

class MemoryFabric:
    def __init__(self) -> None:
        self.store_dir: Path = CONFIG.data_dir / "memory"
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.store_dir / "index.json"
        self._index: dict[str, dict[str, Any]] = self._load_index()
        self._vectorizer = TfidfVectorizer(stop_words='english')

    def lookup(self, query: str) -> dict[str, Any] | None:
        if not CONFIG.cache_enabled or len(self._index) == 0: return None
        
        # Exact match check
        exact_key = self._key(query)
        if exact_key in self._index:
            entry = self._index[exact_key]
            if time.time() - entry["ts"] <= CONFIG.cache_ttl_sec: return entry

        # Semantic match check (TF-IDF)
        try:
            queries = [item["query"] for item in self._index.values()]
            if len(queries) < 2: return None
            
            tfidf_matrix = self._vectorizer.fit_transform(queries + [query])
            cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
            
            best_match_idx = np.argmax(cosine_sim[0])
            if cosine_sim[0][best_match_idx] > 0.85:  # 85% similarity threshold
                entry = list(self._index.values())[best_match_idx]
                log.info(f"Semantic cache hit (similarity: {cosine_sim[0][best_match_idx]:.2f})")
                if time.time() - entry["ts"] <= CONFIG.cache_ttl_sec: return entry
        except Exception as e:
            log.warning(f"Semantic cache check failed: {e}")
            
        return None

    def store(self, query: str, answer: str, metadata: dict | None = None) -> None:
        key = self._key(query)
        self._index[key] = {"query": query, "answer": answer, "metadata": metadata or {}, "ts": time.time()}
        self._save_index()

    def stats(self) -> dict[str, int]:
        return {"entries": len(self._index)}

    @staticmethod
    def _key(query: str) -> str:
        return hashlib.sha256(query.strip().lower().encode()).hexdigest()[:16]

    def _load_index(self) -> dict[str, dict[str, Any]]:
        if self.index_file.exists():
            try: return json.loads(self.index_file.read_text(encoding="utf-8"))
            except: return {}
        return {}

    def _save_index(self) -> None:
        try: self.index_file.write_text(json.dumps(self._index, indent=2), encoding="utf-8")
        except Exception as exc: log.error(f"Failed to save memory: {exc}")
