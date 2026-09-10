"""Lightweight local RAG retrieval for the AI Medical Report Explainer.

This implementation deliberately keeps retrieval local so testing the app does not
consume another Gemini API request just to search the knowledge base.
"""
from __future__ import annotations

import math
import re
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = BASE_DIR / "data" / "medical_knowledge"

_STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "have", "has", "are",
    "was", "were", "into", "your", "you", "patient", "report", "test", "tests",
    "value", "normal", "range", "level", "levels", "than", "then", "they", "their",
    "there", "about", "also", "only", "more", "less", "may", "can", "not", "but",
    "all", "any", "per", "due", "such", "other", "these", "those", "what", "which",
}


def _tokens(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{1,}", text.lower())
    return [w for w in words if w not in _STOPWORDS]


def _split_chunks(text: str, max_words: int = 180, overlap: int = 35) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    step = max_words - overlap
    for start in range(0, len(words), step):
        chunk = " ".join(words[start:start + max_words]).strip()
        if chunk:
            chunks.append(chunk)
        if start + max_words >= len(words):
            break
    return chunks


def _load_documents() -> list[dict]:
    documents = []
    if not KNOWLEDGE_DIR.exists():
        return documents

    for path in sorted(KNOWLEDGE_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for index, chunk in enumerate(_split_chunks(text)):
            documents.append({
                "source": path.name,
                "chunk_id": index,
                "text": chunk,
            })
    return documents


def _idf(documents: list[dict]) -> dict[str, float]:
    df = Counter()
    for doc in documents:
        df.update(set(_tokens(doc["text"])))
    n = max(len(documents), 1)
    return {term: math.log((1 + n) / (1 + freq)) + 1.0 for term, freq in df.items()}


def _vector(text: str, idf: dict[str, float]) -> dict[str, float]:
    counts = Counter(_tokens(text))
    total = sum(counts.values()) or 1
    return {term: (count / total) * idf.get(term, 1.0) for term, count in counts.items()}


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(value * b.get(key, 0.0) for key, value in a.items())
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def build_rag_index() -> dict:
    """Build a small in-memory TF-IDF retrieval index from local medical notes."""
    documents = _load_documents()
    idf = _idf(documents)
    vectors = [_vector(doc["text"], idf) for doc in documents]
    return {"documents": documents, "idf": idf, "vectors": vectors}


def retrieve_context(report_text: str, top_k: int = 5) -> list[dict]:
    """Retrieve the most relevant local medical-knowledge chunks for a report."""
    index = build_rag_index()
    documents = index["documents"]
    if not documents:
        return []

    query_vector = _vector(report_text, index["idf"])
    scored = []
    for doc, vector in zip(documents, index["vectors"]):
        score = _cosine(query_vector, vector)
        scored.append((score, doc))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [
        {**doc, "score": round(score, 4)}
        for score, doc in scored[:max(1, top_k)]
        if score > 0
    ]


def format_context(results: list[dict]) -> str:
    if not results:
        return "No relevant local medical knowledge was retrieved."
    blocks = []
    for item in results:
        blocks.append(
            f"SOURCE: {item['source']}\n"
            f"RELEVANCE: {item['score']}\n"
            f"CONTENT: {item['text']}"
        )
    return "\n\n---\n\n".join(blocks)
