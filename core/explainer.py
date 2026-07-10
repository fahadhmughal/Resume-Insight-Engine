"""Score explanation via keyword-level similarity attribution."""

from typing import Dict, List, Tuple

from core.embedding_engine import embed_text, cosine_similarity_score


def get_score_contributors(
    jd_keywords: List[Tuple[str, float]],
    resume_text: str,
    top_k: int = 5,
) -> Dict[str, List[Tuple[str, float]]]:
    """Identify which JD keywords are strongest/weakest in the resume.

    For each keyword from the JD, embeds it individually and computes
    cosine similarity against the resume text embedding. Keywords with
    the highest similarity are boosters (well-covered), and those with
    the lowest are draggers (gaps or missing skills).

    Similarity scores are on a 0-100 scale.
    """
    if not jd_keywords or not resume_text or not resume_text.strip():
        return {"boosters": [], "draggers": []}

    resume_embedding = embed_text(resume_text)

    keyword_similarities: List[Tuple[str, float]] = []
    for keyword, _relevance in jd_keywords:
        kw_embedding = embed_text(keyword)
        raw_sim = cosine_similarity_score(kw_embedding, resume_embedding)
        score = max(0.0, min(100.0, (raw_sim + 1.0) / 2.0 * 100.0))
        keyword_similarities.append((keyword, round(score, 2)))

    sorted_desc = sorted(keyword_similarities, key=lambda x: x[1], reverse=True)
    boosters = sorted_desc[:top_k]

    sorted_asc = sorted(keyword_similarities, key=lambda x: x[1])
    draggers = sorted_asc[:top_k]

    return {
        "boosters": boosters,
        "draggers": draggers,
    }
