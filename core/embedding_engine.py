"""Sentence embedding utilities using sentence-transformers."""

import os

# Prevent transformers from loading TensorFlow (not needed; avoids memory issues)
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("USE_TF", "0")

import numpy as np
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Model caching
# ---------------------------------------------------------------------------
# In a Streamlit context we use @st.cache_resource for efficient caching
# across reruns. Outside Streamlit (tests, CLI) we use a module-level
# singleton so the model is loaded only once per process.

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
        return SentenceTransformer("all-MiniLM-L6-v2")

except ImportError:
    _load_model_streamlit = None  # type: ignore[assignment]


def _get_model() -> SentenceTransformer:
    """Return the SentenceTransformer model, preferring Streamlit cache."""
    try:
        import streamlit.runtime.scriptrunner as _sr
        ctx = _sr.get_script_run_ctx()
        if ctx is not None and _load_model_streamlit is not None:
            return _load_model_streamlit()
    except Exception:
        pass
    return _load_model()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def embed_text(text: str) -> np.ndarray:
    """Encode a text string into a dense embedding vector.

    Args:
        text: Input text (can be any length; the model handles truncation).

    Returns:
        1-D numpy array of shape (384,) for all-MiniLM-L6-v2.
    """
    if not text or not text.strip():
        # Return a zero vector for empty input so downstream cosine
        # similarity returns 0.0 rather than raising an error.
        model = _get_model()
        dim = model.get_sentence_embedding_dimension()
        return np.zeros(dim, dtype=np.float32)

    model = _get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.astype(np.float32)


def cosine_similarity_score(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors.

    Args:
        vec_a: First embedding vector.
        vec_b: Second embedding vector.

    Returns:
        Cosine similarity in [-1, 1]. Returns 0.0 if either vector is
        all zeros (i.e. from empty text).
    """
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
