"""Test script for the PDF report generator."""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from services.report_generator import generate_candidate_report


SAMPLE_SECTION_SCORES = {
    "skills": 79.47,
    "experience": 84.30,
    "projects": 67.87,
    "education": 66.78,
    "certifications": 0.0,
}

SAMPLE_BOOSTERS = [
    ("data pipelines", 81.08),
    ("apache spark", 73.98),
    ("data warehousing", 70.99),
    ("etl processing", 70.37),
    ("aws cloud", 66.47),
]

SAMPLE_DRAGGERS = [
    ("blockchain smart contracts", 48.68),
    ("react frontend", 53.15),
    ("agile scrum methodology", 53.53),
    ("embedded systems firmware", 56.10),
    ("ios swift development", 56.92),
]


def main():
    print("Generating sample candidate report...")

    pdf_bytes = generate_candidate_report(
        candidate_name="resume_alice_chen.pdf",
        final_score=78.98,
        section_scores=SAMPLE_SECTION_SCORES,
        boosters=SAMPLE_BOOSTERS,
        draggers=SAMPLE_DRAGGERS,
    )

    output_path = os.path.join(PROJECT_ROOT, "sample_data", "test_report.pdf")
    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    file_size_kb = len(pdf_bytes) / 1024
    print(f"Report saved to: {output_path}")
    print(f"File size: {file_size_kb:.1f} KB")

    # Sanity checks
    assert len(pdf_bytes) > 0, "PDF should not be empty."
    assert pdf_bytes[:5] == b"%PDF-", "File should start with PDF header."
    assert file_size_kb < 500, "Single-page report should be under 500 KB."

    print("All checks passed.")


if __name__ == "__main__":
    main()
