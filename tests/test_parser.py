"""Test script for the resume parser and section splitter."""

import os
import sys

# Ensure the project root is on the path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from core.parser import extract_text_from_pdf, ParserError
from core.section_splitter import split_into_sections
from tests.generate_sample_resume import create_sample_resume


SAMPLE_PDF = os.path.join(PROJECT_ROOT, "sample_data", "sample_resume.pdf")


def ensure_sample_pdf():
    """Generate the sample PDF if it does not already exist."""
    if not os.path.exists(SAMPLE_PDF):
        print(f"Generating sample resume at {SAMPLE_PDF} ...")
        create_sample_resume(SAMPLE_PDF)


def test_extract_text():
    """Test that text extraction returns non-empty content."""
    print("--- extract_text_from_pdf ---")
    with open(SAMPLE_PDF, "rb") as f:
        text = extract_text_from_pdf(f)
    assert text, "Extracted text should not be empty."
    print(f"Extracted {len(text)} characters.\n")
    return text


def test_validation_rejects_non_pdf(tmp_dir):
    """Test that a non-PDF file is rejected."""
    print("--- validation: non-PDF rejection ---")
    fake_path = os.path.join(tmp_dir, "fake.txt")
    with open(fake_path, "w") as f:
        f.write("not a pdf")
    try:
        with open(fake_path, "rb") as f:
            extract_text_from_pdf(f)
        print("FAIL: should have raised ParserError for non-PDF file.\n")
    except ParserError as e:
        print(f"OK: {e}\n")


def test_validation_rejects_empty_pdf(tmp_dir):
    """Test that an empty file is rejected."""
    print("--- validation: empty file rejection ---")
    empty_path = os.path.join(tmp_dir, "empty.pdf")
    with open(empty_path, "wb") as f:
        pass  # 0 bytes
    try:
        with open(empty_path, "rb") as f:
            extract_text_from_pdf(f)
        print("FAIL: should have raised ParserError for empty file.\n")
    except ParserError as e:
        print(f"OK: {e}\n")


def test_split_into_sections(text):
    """Test that sections are detected correctly."""
    print("--- split_into_sections ---")
    sections = split_into_sections(text)

    for name, content in sections.items():
        status = "FOUND" if content else "EMPTY"
        preview = content[:120].replace("\n", " ") if content else ""
        print(f"  [{status}] {name}: {preview}{'...' if len(content) > 120 else ''}")

    print()

    # Verify that at least Skills and Experience are non-empty
    assert sections["skills"], "Skills section should not be empty."
    assert sections["experience"], "Experience section should not be empty."
    print("Skills and Experience sections are non-empty: OK\n")

    return sections


def main():
    ensure_sample_pdf()

    # Create a temp dir for validation tests
    tmp_dir = os.path.join(PROJECT_ROOT, "sample_data", "_test_tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    try:
        test_validation_rejects_non_pdf(tmp_dir)
        test_validation_rejects_empty_pdf(tmp_dir)
        text = test_extract_text()
        test_split_into_sections(text)
        print("All tests passed.")
    finally:
        # Clean up temp files
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
