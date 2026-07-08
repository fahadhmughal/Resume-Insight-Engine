"""Scoring engine: compute per-section and weighted composite resume scores."""

from typing import Dict

from core.embedding_engine import embed_text, cosine_similarity_score

# ---------------------------------------------------------------------------
# Section weights (must sum to 1.0)
# ---------------------------------------------------------------------------
# These weights reflect the relative importance of each resume section
# when evaluating fit against a job description.
SECTION_WEIGHTS: Dict[str, float] = {
    "skills":         0.45,
    "experience":     0.35,
    "projects":       0.10,
    "education":      0.08,
    "certifications": 0.02,
}


def compute_section_scores(
    jd_text: str,
    resume_sections: Dict[str, str],
) -> Dict[str, float]:
    """Embed the JD and each resume section, returning per-section similarity.

    Each score is on a 0-100 scale (cosine similarity mapped from [-1,1]
    to [0,100]).  Sections that are missing or empty receive a score of 0.

    Args:
        jd_text:          Plain-text job description.
        resume_sections:  Dict with keys like "skills", "experience", etc.

    Returns:
        Dict mapping section name -> similarity score (0-100).
    """
    jd_embedding = embed_text(jd_text)

    scores: Dict[str, float] = {}
    for section_name in SECTION_WEIGHTS:
        section_text = resume_sections.get(section_name, "")
        if not section_text or not section_text.strip():
            scores[section_name] = 0.0
            continue
        section_embedding = embed_text(section_text)
        raw_sim = cosine_similarity_score(jd_embedding, section_embedding)
        # Map cosine similarity from [-1, 1] to [0, 100].
        # In practice, similarity between meaningful texts is rarely
        # negative, so this mainly shifts the range upward.
        score = max(0.0, min(100.0, (raw_sim + 1.0) / 2.0 * 100.0))
        scores[section_name] = round(score, 2)

    return scores


def compute_final_score(section_scores: Dict[str, float]) -> float:
    """Compute a weighted composite score from per-section scores.

    Weight redistribution logic for missing sections:
    -------------------------------------------------
    If a section has a score of 0 AND the corresponding section text was
    empty (i.e. not found in the resume), its weight should not penalise
    the candidate. Instead, that section's weight is redistributed
    *proportionally* across the remaining present sections.

    Example: if "certifications" (weight 0.02) and "projects" (weight 0.10)
    are missing, the remaining weights (skills=0.45, experience=0.35,
    education=0.08, total=0.88) are each scaled by 1.0/0.88 so they sum
    to 1.0.

    A section is considered "present" if its score is > 0.

    Args:
        section_scores: Dict mapping section name -> score (0-100).

    Returns:
        Weighted composite score on 0-100 scale.
    """
    # Identify which sections are present (score > 0)
    present_weights: Dict[str, float] = {}
    for section, weight in SECTION_WEIGHTS.items():
        if section_scores.get(section, 0.0) > 0.0:
            present_weights[section] = weight

    total_present_weight = sum(present_weights.values())

    if total_present_weight == 0.0:
        # No sections matched at all
        return 0.0

    # Scale factor to redistribute missing weight proportionally
    # e.g. if total_present_weight = 0.88, scale_factor = 1.0 / 0.88 = 1.136
    scale_factor = 1.0 / total_present_weight

    weighted_sum = 0.0
    for section, weight in present_weights.items():
        adjusted_weight = weight * scale_factor
        weighted_sum += adjusted_weight * section_scores[section]

    return round(weighted_sum, 2)
