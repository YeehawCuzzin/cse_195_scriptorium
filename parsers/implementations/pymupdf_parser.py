from __future__ import annotations

from parsers.core.base import ParserError, ParserResult, require_pdf


PARSER_NAME = "pymupdf"
CATEGORY = "flat_text"


def extract(pdf_path: str) -> ParserResult:
    """
    Extract plain text from a PDF using PyMuPDF.

    PyMuPDF is a fast flat-text baseline parser. It is useful for speed and
    simple text extraction, but it does not preserve rich semantic structure
    such as section hierarchy, tables, figures, or layout relationships.
    """

    pdf = require_pdf(pdf_path)

    try:
        import fitz
    except ModuleNotFoundError as exc:
        raise ParserError(
            "Python package 'pymupdf' is not installed. Install it with: pip install pymupdf"
        ) from exc

    pages = []

    with fitz.open(str(pdf)) as doc:
        page_count = len(doc)

        for i, page in enumerate(doc, start=1):
            text = page.get_text("text")
            pages.append(f"\n--- PAGE {i} ---\n{text}")

    output_text = "\n".join(pages)

    return ParserResult(
        parser_name=PARSER_NAME,
        text=output_text,
        category=CATEGORY,
        output_format="text",
        metadata={
            "source_file": str(pdf),
            "page_count": page_count,
        },
        artifacts=[],
        raw=None,
    )