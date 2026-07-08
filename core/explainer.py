"""Score explanation via keyword-level similarity attribution.

This module computes per-keyword cosine similarity between individual JD
keywords and the full resume text embedding. It identifies which JD
keywords are well-represented in the resume (boosters) and which are
weakly represented or absent (draggers).

This is NOT SHAP-based attribution. It is a straightforward per-keyword
cosine similarity comparison against the resume embedding.
"""

from typing import Dict, List, Tuple

from core.embedding_engine import embed_text, cosine_similarity_score


def get_score_contributors(
    jd_keywords: List[Tuple[str, float]],
    resume_text: str,
    top_k: int = 5,
) -> Dict[str, List[Tuple[str, float]]]:
    """Identify which JD keywords are strongest/weakest in the resume.

    For each keyword from the JD, we embed it individually and compute
    cosine similarity against the resume text embedding. Keywords with
    the highest similarity are "boosters" (well-covered by the resume),
    and those with the lowest similarity are "draggers" (gaps or missing
    skills).

    Methodology: keyword-level similarity attribution using cosine
    similarity between sentence embeddings.

    Args:
        jd_keywords:  List of (keyword, relevance_score) tuples as returned
                      by extract_jd_keywords. The relevance_score from
                      KeyBERT is not used in similarity computation but is
                      preserved for reference.
        resume_text:  Full plain-text resume content (all sections combined).
        top_k:        Number of boosters and draggers to return.

    Returns:
        Dict with two keys:
            "boosters": top_k keywords with highest similarity to the resume,
                        as [(keyword, similarity_score), ...] in descending
                        order.
            "draggers": top_k keywords with lowest similarity to the resume,
                        as [(keyword, similarity_score), ...] in ascending
                        order.
        Similarity scores are on a 0-100 scale.
    """
    if not jd_keywords or not resume_text or not resume_text.strip():
        return {"boosters": [], "draggers": []}

    resume_embedding = embed_text(resume_text)

    # Compute similarity for each JD keyword against the resume
    keyword_similarities: List[Tuple[str, float]] = []
    for keyword, _relevance in jd_keywords:
        kw_embedding = embed_text(keyword)
        raw_sim = cosine_similarity_score(kw_embedding, resume_embedding)
        # Map from [-1, 1] to [0, 100], consistent with scoring_engine
        score = max(0.0, min(100.0, (raw_sim + 1.0) / 2.0 * 100.0))
        keyword_similarities.append((keyword, round(score, 2)))

    # Sort by similarity descending for boosters
    sorted_desc = sorted(keyword_similarities, key=lambda x: x[1], reverse=True)
    boosters = sorted_desc[:top_k]

    # Sort by similarity ascending for draggers
    sorted_asc = sorted(keyword_similarities, key=lambda x: x[1])
    draggers = sorted_asc[:top_k]

    return {
        "boosters": boosters,
        "draggers": draggers,
    }
