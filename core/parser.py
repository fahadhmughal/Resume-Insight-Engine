"""PDF text extraction with validation."""

import pdfplumber
import re


MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024


class ParserError(Exception):
    """Raised when PDF parsing fails validation or extraction."""
    pass


def _validate_file(file) -> None:
    """Validate that the uploaded file is a non-empty PDF under 5 MB."""
    filename = getattr(file, "name", "")
    if not filename.lower().endswith(".pdf"):
        raise ParserError(
            f"Invalid file type: '{filename}'. Only PDF files are accepted."
        )

    current_pos = file.tell()
    file.seek(0, 2)
    size = file.tell()
    file.seek(current_pos)

    if size == 0:
        raise ParserError("The uploaded PDF file is empty (0 bytes).")

    if size > MAX_FILE_SIZE_BYTES:
        size_mb = size / (1024 * 1024)
        raise ParserError(
            f"File size ({size_mb:.1f} MB) exceeds the 5 MB limit."
        )


def _clean_text(raw_text: str) -> str:
    """Collapse excessive whitespace and blank lines while preserving structure."""
    text = raw_text.replace("\t", " ")
    text = re.sub(r"[^\S\n]+", " ", text)
    text = re.sub(r" *\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    return text


def extract_text_from_pdf(file) -> str:
    """Extract and clean plain text from a PDF file.

    Handles multi-page PDFs by concatenating page text in order.
    """
    _validate_file(file)

    file.seek(0)
    pages_text = []

    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
    except Exception as exc:
        raise ParserError(f"Failed to read PDF: {exc}") from exc

    if not pages_text:
        raise ParserError(
            "The PDF contains no extractable text. "
            "It may be a scanned image; OCR is not currently supported."
        )

    combined = "\n".join(pages_text)
    return _clean_text(combined)
