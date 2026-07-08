"""Split resume text into named sections using header keyword matching."""

import re
from typing import Dict

import spacy

# Lazy-loaded spaCy model
_nlp = None


def _get_nlp():
    """Load spaCy model on first use."""
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


# Canonical section names and the header keywords that map to each one.
# All keywords are compared case-insensitively.
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

# Build a flat lookup: normalised keyword -> canonical section name
_KEYWORD_TO_SECTION: Dict[str, str] = {}
for section, keywords in SECTION_KEYWORDS.items():
    for kw in keywords:
        _KEYWORD_TO_SECTION[kw.lower()] = section


def _is_header_line(line: str) -> str | None:
    """Check whether a line looks like a section header.

    A header line is one whose meaningful content (after stripping
    punctuation, numbering, and whitespace) matches a known keyword.

    Args:
        line: A single line of text.

    Returns:
        The canonical section name if the line is a header, else None.
    """
    # Strip the line
    cleaned = line.strip()
    if not cleaned:
        return None

    # Remove common decorations: leading/trailing dashes, colons, pipes, numbers
    cleaned = re.sub(r"^[\d.\-|:]+", "", cleaned)
    cleaned = re.sub(r"[\-|:]+$", "", cleaned)
    cleaned = cleaned.strip()

    if not cleaned:
        return None

    normalised = cleaned.lower()
    return _KEYWORD_TO_SECTION.get(normalised)


def _segment_with_spacy(text: str) -> str:
    """Use spaCy sentence segmentation to produce clean sentence-separated text.

    This improves readability of section content that was extracted from PDF
    layout where line breaks don't necessarily correspond to sentence ends.

    Args:
        text: Raw section text.

    Returns:
        Text with sentences separated by single newlines.
    """
    if not text.strip():
        return ""

    nlp = _get_nlp()
    # Limit to 100 000 chars to stay within spaCy defaults
    truncated = text[:100_000]
    doc = nlp(truncated)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    return "\n".join(sentences)


def split_into_sections(text: str) -> Dict[str, str]:
    """Split resume text into canonical sections.

    Scans the text line-by-line for section headers. Everything between
    one header and the next (or end of text) is assigned to that section.
    Content that appears before the first recognised header is discarded
    (it is typically the candidate's name / contact info).

    Each section's content is post-processed with spaCy sentence
    segmentation for cleaner output.

    Args:
        text: Plain-text resume content (as returned by extract_text_from_pdf).

    Returns:
        A dict with keys: skills, experience, education, projects,
        certifications. Values are the section text (or empty string if
        that section was not found).
    """
    # Initialise all sections as empty
    result: Dict[str, str] = {section: "" for section in SECTION_KEYWORDS}

    lines = text.split("\n")
    current_section = None
    current_lines: list = []

    for line in lines:
        detected = _is_header_line(line)
        if detected is not None:
            # Flush accumulated lines into the previous section
            if current_section is not None:
                raw = "\n".join(current_lines).strip()
                result[current_section] = _segment_with_spacy(raw)
            current_section = detected
            current_lines = []
        else:
            if current_section is not None:
                current_lines.append(line)

    # Flush the last section
    if current_section is not None:
        raw = "\n".join(current_lines).strip()
        result[current_section] = _segment_with_spacy(raw)

    return result
