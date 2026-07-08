"""Job description keyword extraction using KeyBERT."""

import os
import re
from typing import List, Tuple

# Prevent transformers from loading TensorFlow (not needed; avoids memory issues)
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("USE_TF", "0")

from keybert import KeyBERT

# ---------------------------------------------------------------------------
# Model caching
# ---------------------------------------------------------------------------
# In a Streamlit context we use @st.cache_resource for efficient model caching
# across reruns.  Outside Streamlit (e.g. tests, CLI) we fall back to a plain
# module-level singleton so the model is only loaded once per process.

_keybert_model = None


def _load_model() -> KeyBERT:
    """Load (or return cached) KeyBERT model with all-MiniLM-L6-v2."""
    global _keybert_model
    if _keybert_model is None:
        _keybert_model = KeyBERT(model="all-MiniLM-L6-v2")
    return _keybert_model


try:
    import streamlit as st

    @st.cache_resource
    def _load_model_streamlit() -> KeyBERT:
        """Streamlit-cached model loader."""
        return KeyBERT(model="all-MiniLM-L6-v2")

except ImportError:
    _load_model_streamlit = None  # type: ignore[assignment]


def _get_model() -> KeyBERT:
    """Return the KeyBERT model, using Streamlit caching when available."""
    try:
        import streamlit.runtime.scriptrunner as _sr
        # If we can access the script run context we are inside Streamlit
        ctx = _sr.get_script_run_ctx()
        if ctx is not None and _load_model_streamlit is not None:
            return _load_model_streamlit()
    except Exception:
        pass
    return _load_model()


# ---------------------------------------------------------------------------
# Stopword set (lightweight, no extra dependency)
# ---------------------------------------------------------------------------
_STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "shall", "should", "may", "might", "must", "can", "could",
    "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
    "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "each",
    "every", "both", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "just", "because", "about", "up", "if", "it", "its", "this", "that",
    "these", "those", "i", "me", "my", "we", "our", "you", "your", "he",
    "him", "his", "she", "her", "they", "them", "their", "what", "which",
    "who", "whom", "also", "etc", "per", "via", "e.g", "i.e",
})


def _is_stopword_only(phrase: str) -> bool:
    """Return True if every token in the phrase is a stopword."""
    tokens = re.findall(r"[a-z]+", phrase.lower())
    return all(t in _STOPWORDS for t in tokens) if tokens else True


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_jd_keywords(
    jd_text: str,
    top_n: int = 20,
) -> List[Tuple[str, float]]:
    """Extract the most relevant keyphrases from a job description.

    Uses KeyBERT (backed by all-MiniLM-L6-v2) to produce candidate
    keyphrases, then deduplicates and filters out stopword-only entries.

    Args:
        jd_text:  Plain-text job description.
        top_n:    Maximum number of keyphrases to return.

    Returns:
        A list of (keyphrase, score) tuples sorted by descending score.
        Scores are cosine-similarity values in roughly [0, 1].
    """
    if not jd_text or not jd_text.strip():
        return []

    model = _get_model()

    # Extract more candidates than needed so we still have enough after
    # filtering.  Use 1-3 word n-gram range for meaningful phrases.
    raw_keywords = model.extract_keywords(
        jd_text,
        keyphrase_ngram_range=(1, 3),
        stop_words="english",
        use_mmr=True,       # Maximal Marginal Relevance for diversity
        diversity=0.5,
        top_n=top_n * 3,    # over-fetch to compensate for filtering
    )

    # Deduplicate (case-insensitive) and filter
    seen: set = set()
    results: List[Tuple[str, float]] = []

    for phrase, score in raw_keywords:
        normalised = phrase.lower().strip()
        if normalised in seen:
            continue
        if _is_stopword_only(normalised):
            continue
        seen.add(normalised)
        results.append((phrase, round(score, 4)))
        if len(results) >= top_n:
            break

    # Sort descending by score (should already be, but ensure)
    results.sort(key=lambda x: x[1], reverse=True)
    return results
