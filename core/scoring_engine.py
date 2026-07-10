"""Scoring engine: compute per-section and weighted composite resume scores."""

from typing import Dict

from core.embedding_engine import embed_text, cosine_similarity_score

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

    Each score is on a 0-100 scale. Sections that are missing or empty
    receive a score of 0.
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
        score = max(0.0, min(100.0, (raw_sim + 1.0) / 2.0 * 100.0))
        scores[section_name] = round(score, 2)

    return scores


def compute_final_score(section_scores: Dict[str, float]) -> float:
    """Compute a weighted composite score from per-section scores.

    If a section has a score of 0 (not found in the resume), its weight
    is redistributed proportionally across the remaining present sections.
    """
    present_weights: Dict[str, float] = {}
    for section, weight in SECTION_WEIGHTS.items():
        if section_scores.get(section, 0.0) > 0.0:
            present_weights[section] = weight

    total_present_weight = sum(present_weights.values())

    if total_present_weight == 0.0:
        return 0.0

    scale_factor = 1.0 / total_present_weight

    weighted_sum = 0.0
    for section, weight in present_weights.items():
        adjusted_weight = weight * scale_factor
        weighted_sum += adjusted_weight * section_scores[section]

    return round(weighted_sum, 2)
