from __future__ import annotations

from parsers.core.base import ParserError, ParserResult, require_pdf


PARSER_NAME = "pypdf"
CATEGORY = "flat_text"


def extract(pdf_path: str) -> ParserResult:
    """
    Extract plain text from a PDF using PyPDF.

    PyPDF is a lightweight flat-text parser. It is useful as a simple baseline,
    but it usually does not preserve rich document structure such as headings,
    tables, figures, or layout relationships.
    """

    pdf = require_pdf(pdf_path)

    try:
        from pypdf import PdfReader
    except ModuleNotFoundError as exc:
        raise ParserError(
            "Python package 'pypdf' is not installed. Install it with: pip install pypdf"
        ) from exc

    reader = PdfReader(str(pdf))
    pages = []

    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append(f"\n--- PAGE {i} ---\n{text}")

    output_text = "\n".join(pages)

    return ParserResult(
        parser_name=PARSER_NAME,
        text=output_text,
        category=CATEGORY,
        output_format="text",
        metadata={
            "source_file": str(pdf),
            "page_count": len(reader.pages),
        },
        artifacts=[],
        raw=None,
    )