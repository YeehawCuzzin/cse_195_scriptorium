from __future__ import annotations

from parsers.core.base import ParserError, ParserResult, require_pdf


PARSER_NAME = "pdfplumber"
CATEGORY = "flat_text"


def extract(pdf_path: str) -> ParserResult:
    """
    Extract plain text from a PDF using pdfplumber.

    pdfplumber is useful as a flat-text baseline with some layout awareness,
    but it can still struggle with multi-column academic PDFs, tables, figures,
    and complex formatting.
    """

    pdf_path_obj = require_pdf(pdf_path)

    try:
        import pdfplumber
    except ModuleNotFoundError as exc:
        raise ParserError(
            "Python package 'pdfplumber' is not installed. Install it with: pip install pdfplumber"
        ) from exc

    pages = []

    with pdfplumber.open(str(pdf_path_obj)) as pdf:
        page_count = len(pdf.pages)

        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append(f"\n--- PAGE {i} ---\n{text}")

    output_text = "\n".join(pages)

    return ParserResult(
        parser_name=PARSER_NAME,
        text=output_text,
        category=CATEGORY,
        output_format="text",
        metadata={
            "source_file": str(pdf_path_obj),
            "page_count": page_count,
        },
        artifacts=[],
        raw=None,
    )