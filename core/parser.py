"""PDF text extraction with validation."""

import pdfplumber
import re


# Maximum file size: 5 MB
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024


class ParserError(Exception):
    """Raised when PDF parsing fails validation or extraction."""
    pass


def _validate_file(file) -> None:
    """Validate that the uploaded file is a non-empty PDF under 5 MB.

    Args:
        file: A file-like object (e.g. Streamlit UploadedFile or open file handle).

    Raises:
        ParserError: If the file fails any validation check.
    """
    # Check file name for .pdf extension
    filename = getattr(file, "name", "")
    if not filename.lower().endswith(".pdf"):
        raise ParserError(
            f"Invalid file type: '{filename}'. Only PDF files are accepted."
        )

    # Check file size
    current_pos = file.tell()
    file.seek(0, 2)  # seek to end
    size = file.tell()
    file.seek(current_pos)  # restore position

    if size == 0:
        raise ParserError("The uploaded PDF file is empty (0 bytes).")

    if size > MAX_FILE_SIZE_BYTES:
        size_mb = size / (1024 * 1024)
        raise ParserError(
            f"File size ({size_mb:.1f} MB) exceeds the 5 MB limit."
        )


def _clean_text(raw_text: str) -> str:
    """Collapse excessive whitespace and blank lines while preserving structure.

    Args:
        raw_text: The raw extracted text from pdfplumber.

    Returns:
        Cleaned text with normalised whitespace.
    """
    # Replace tabs with spaces
    text = raw_text.replace("\t", " ")
    # Collapse runs of spaces (but not newlines) into a single space
    text = re.sub(r"[^\S\n]+", " ", text)
    # Strip trailing spaces on each line
    text = re.sub(r" *\n", "\n", text)
    # Collapse 3+ consecutive newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def extract_text_from_pdf(file) -> str:
    """Extract and clean plain text from a PDF file.

    Handles multi-page PDFs by concatenating page text in order.

    Args:
        file: A file-like object with a `.name` attribute (e.g. an open
              binary file or a Streamlit UploadedFile).

    Returns:
        Cleaned plain-text content of the PDF.

    Raises:
        ParserError: If the file is invalid or contains no extractable text.
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
