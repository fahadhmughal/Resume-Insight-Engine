"""Split resume text into named sections using header keyword matching."""

import re
from typing import Dict

import spacy

_nlp = None


def _get_nlp():
    """Load spaCy model on first use."""
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


SECTION_KEYWORDS: Dict[str, list] = {
    "skills": [
        "skills",
        "technical skills",
        "core competencies",
        "competencies",
        "key skills",
        "areas of expertise",
        "technologies",
        "tools and technologies",
        "proficiencies",
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
        "career history",
        "relevant experience",
    ],
    "education": [
        "education",
        "academic background",
        "academic qualifications",
        "qualifications",
        "educational background",
    ],
    "projects": [
        "projects",
        "personal projects",
        "academic projects",
        "key projects",
        "selected projects",
    ],
    "certifications": [
        "certifications",
        "certificates",
        "licenses",
        "licenses and certifications",
        "certifications and licenses",
        "professional certifications",
        "credentials",
    ],
}

_KEYWORD_TO_SECTION: Dict[str, str] = {}
for section, keywords in SECTION_KEYWORDS.items():
    for kw in keywords:
        _KEYWORD_TO_SECTION[kw.lower()] = section


def _is_header_line(line: str) -> str | None:
    """Check whether a line looks like a section header.

    Returns the canonical section name if the line is a header, else None.
    """
    cleaned = line.strip()
    if not cleaned:
        return None

    cleaned = re.sub(r"^[\d.\-|:]+", "", cleaned)
    cleaned = re.sub(r"[\-|:]+$", "", cleaned)
    cleaned = cleaned.strip()

    if not cleaned:
        return None

    normalised = cleaned.lower()
    return _KEYWORD_TO_SECTION.get(normalised)


def _segment_with_spacy(text: str) -> str:
    """Use spaCy sentence segmentation to produce clean sentence-separated text."""
    if not text.strip():
        return ""

    nlp = _get_nlp()
    truncated = text[:100_000]
    doc = nlp(truncated)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    return "\n".join(sentences)


def split_into_sections(text: str) -> Dict[str, str]:
    """Split resume text into canonical sections.

    Scans the text line-by-line for section headers. Content between
    one header and the next is assigned to that section. Content before
    the first header is discarded (typically name/contact info).

    Each section is post-processed with spaCy sentence segmentation.
    """
    result: Dict[str, str] = {section: "" for section in SECTION_KEYWORDS}

    lines = text.split("\n")
    current_section = None
    current_lines: list = []

    for line in lines:
        detected = _is_header_line(line)
        if detected is not None:
            if current_section is not None:
                raw = "\n".join(current_lines).strip()
                result[current_section] = _segment_with_spacy(raw)
            current_section = detected
            current_lines = []
        else:
            if current_section is not None:
                current_lines.append(line)

    if current_section is not None:
        raw = "\n".join(current_lines).strip()
        result[current_section] = _segment_with_spacy(raw)

    return result
