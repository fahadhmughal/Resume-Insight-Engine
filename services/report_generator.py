"""PDF report generation for individual candidate results."""

import io
from typing import Dict, List, Tuple

from fpdf import FPDF

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
NAVY = (27, 42, 74)
WHITE = (255, 255, 255)
DARK_GREY = (74, 74, 74)
MID_GREY = (107, 114, 128)
LIGHT_GREY = (229, 231, 235)
GREEN_BG = (209, 250, 229)
GREEN_TEXT = (6, 95, 70)
AMBER_BG = (254, 243, 199)
AMBER_TEXT = (146, 64, 14)
RED_BG = (254, 226, 226)
RED_TEXT = (153, 27, 27)

SECTION_LABELS = {
    "skills": "Skills",
    "experience": "Experience",
    "projects": "Projects",
    "education": "Education",
    "certifications": "Certifications",
}

SECTION_ORDER = ["skills", "experience", "projects", "education", "certifications"]


def _score_color(score: float):
    """Return (bg_rgb, text_rgb) tuple for a given score."""
    if score >= 70:
        return GREEN_BG, GREEN_TEXT
    elif score >= 50:
        return AMBER_BG, AMBER_TEXT
    return RED_BG, RED_TEXT


class _ReportPDF(FPDF):
    """Custom FPDF subclass for candidate reports."""

    def header(self):
        # Navy header bar
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 28, "F")
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*WHITE)
        self.set_y(7)
        self.cell(0, 14, "Resume Insight Engine", align="L")
        self.set_font("Helvetica", "", 9)
        self.cell(0, 14, "Candidate Report", align="R")
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*MID_GREY)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def generate_candidate_report(
    candidate_name: str,
    final_score: float,
    section_scores: Dict[str, float],
    boosters: List[Tuple[str, float]],
    draggers: List[Tuple[str, float]],
) -> bytes:
    """Generate a single-page PDF report for one candidate.

    Args:
        candidate_name:  Filename or name of the candidate.
        final_score:     Weighted composite score (0-100).
        section_scores:  Dict mapping section name to score (0-100).
        boosters:        List of (keyword, score) tuples for matched skills.
        draggers:        List of (keyword, score) tuples for skill gaps.

    Returns:
        PDF file contents as bytes.
    """
    pdf = _ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_margins(15, 15, 15)

    # -----------------------------------------------------------------------
    # Candidate name
    # -----------------------------------------------------------------------
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, candidate_name, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # -----------------------------------------------------------------------
    # Final score
    # -----------------------------------------------------------------------
    bg, fg = _score_color(final_score)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*MID_GREY)
    pdf.cell(30, 7, "Final Score:", new_x="END")
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(*bg)
    pdf.set_text_color(*fg)
    pdf.cell(22, 8, f"{final_score:.1f}", align="C", fill=True,
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # -----------------------------------------------------------------------
    # Section score table
    # -----------------------------------------------------------------------
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 8, "Section Score Breakdown", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Table header
    col_w_name = 70
    col_w_score = 30
    col_w_bar = 80

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(*WHITE)
    pdf.cell(col_w_name, 7, "  Section", fill=True, new_x="END")
    pdf.cell(col_w_score, 7, "Score", align="C", fill=True, new_x="END")
    pdf.cell(col_w_bar, 7, "", fill=True, new_x="LMARGIN", new_y="NEXT")

    # Table rows
    pdf.set_font("Helvetica", "", 9)
    for i, section in enumerate(SECTION_ORDER):
        score = section_scores.get(section, 0.0)
        label = SECTION_LABELS.get(section, section.title())

        # Alternating row background
        if i % 2 == 0:
            pdf.set_fill_color(249, 250, 251)
        else:
            pdf.set_fill_color(*WHITE)

        pdf.set_text_color(*DARK_GREY)
        pdf.cell(col_w_name, 7, f"  {label}", fill=True, new_x="END")

        bg_s, fg_s = _score_color(score)
        pdf.set_text_color(*fg_s)
        pdf.cell(col_w_score, 7, f"{score:.1f}", align="C", fill=True, new_x="END")

        # Score bar
        pdf.set_text_color(*DARK_GREY)
        y = pdf.get_y()
        x = pdf.get_x()
        # Background
        pdf.set_fill_color(240, 242, 246)
        pdf.rect(x, y, col_w_bar, 7, "F")
        # Filled portion
        bar_width = max(0, min(col_w_bar, col_w_bar * score / 100.0))
        pdf.set_fill_color(*bg_s)
        if bar_width > 0:
            pdf.rect(x, y, bar_width, 7, "F")

        pdf.cell(col_w_bar, 7, "", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)

    # -----------------------------------------------------------------------
    # Boosters and Draggers side by side
    # -----------------------------------------------------------------------
    col_width = 88
    start_y = pdf.get_y()

    # -- Boosters (left column) --
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*NAVY)
    pdf.cell(col_width, 8, "Matched Skills", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    if boosters:
        for kw, score in boosters:
            pdf.set_x(15)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*GREEN_TEXT)
            pdf.cell(3, 5, "+", new_x="END")
            pdf.set_text_color(*DARK_GREY)
            pdf.cell(col_width - 25, 5, f" {kw}", new_x="END")
            pdf.set_text_color(*MID_GREY)
            pdf.cell(18, 5, f"({score:.1f})", align="R",
                     new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_x(15)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(*MID_GREY)
        pdf.cell(col_width, 5, "No data available.",
                 new_x="LMARGIN", new_y="NEXT")

    left_end_y = pdf.get_y()

    # -- Draggers (right column) --
    pdf.set_y(start_y)
    pdf.set_x(15 + col_width + 4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*NAVY)
    pdf.cell(col_width, 8, "Skill Gaps", new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(pdf.get_y() + 1)

    if draggers:
        for kw, score in draggers:
            pdf.set_x(15 + col_width + 4)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*RED_TEXT)
            pdf.cell(3, 5, "-", new_x="END")
            pdf.set_text_color(*DARK_GREY)
            pdf.cell(col_width - 25, 5, f" {kw}", new_x="END")
            pdf.set_text_color(*MID_GREY)
            pdf.cell(18, 5, f"({score:.1f})", align="R",
                     new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_x(15 + col_width + 4)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(*MID_GREY)
        pdf.cell(col_width, 5, "No data available.",
                 new_x="LMARGIN", new_y="NEXT")

    right_end_y = pdf.get_y()

    # Move past both columns
    pdf.set_y(max(left_end_y, right_end_y) + 4)

    # -----------------------------------------------------------------------
    # Divider line
    # -----------------------------------------------------------------------
    pdf.set_draw_color(*LIGHT_GREY)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)

    # -----------------------------------------------------------------------
    # Disclaimer
    # -----------------------------------------------------------------------
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*MID_GREY)
    pdf.multi_cell(
        0, 4,
        "Scores are computed using keyword-level similarity attribution "
        "between the job description and resume sections. They are intended "
        "as a screening aid and should not be the sole basis for hiring "
        "decisions.",
    )

    # Output to bytes
    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
