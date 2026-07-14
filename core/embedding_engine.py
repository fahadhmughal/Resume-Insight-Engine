"""Sentence embedding utilities using sentence-transformers."""

import os

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("USE_TF", "0")

import numpy as np
from sentence_transformers import SentenceTransformer

_st_model = None


def _load_model() -> SentenceTransformer:
    """Load (or return cached) SentenceTransformer model."""
    global _st_model
    if _st_model is None:
        _st_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _st_model


try:
    import streamlit as st

    @st.cache_resource
    def _load_model_streamlit() -> SentenceTransformer:
        """Streamlit-cached model loader."""
        model = SentenceTransformer("all-MiniLM-L6-v2")
        try:
            import torch

            device_name = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Resume Insight Engine: torch={torch.__version__}, device={device_name}")
        except Exception as exc:
            print(f"Resume Insight Engine: torch diagnostics unavailable: {exc}")
        return model

except ImportError:
    _load_model_streamlit = None


def get_sentence_transformer_model() -> SentenceTransformer:
    """Return the shared SentenceTransformer model, preferring Streamlit cache."""
    try:
        import streamlit.runtime.scriptrunner as _sr
        ctx = _sr.get_script_run_ctx()
        if ctx is not None and _load_model_streamlit is not None:
            return _load_model_streamlit()
    except Exception:
        pass
    return _load_model()


def embed_text(text: str) -> np.ndarray:
    """Encode a text string into a dense embedding vector.

    Returns a 1-D numpy array of shape (384,) for all-MiniLM-L6-v2.
    """
    if not text or not text.strip():
        model = get_sentence_transformer_model()
        dim = model.get_sentence_embedding_dimension()
        return np.zeros(dim, dtype=np.float32)

    model = get_sentence_transformer_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.astype(np.float32)


def cosine_similarity_score(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors.

    Returns cosine similarity in [-1, 1]. Returns 0.0 if either vector
    is all zeros.
    """
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
