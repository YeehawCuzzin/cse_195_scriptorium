from __future__ import annotations

from parsers.core.base import ParserError, ParserResult, require_pdf


PARSER_NAME = "unstructured"
CATEGORY = "structure_aware"


def extract(pdf_path: str) -> ParserResult:
    """
    Extract structure-aware text from a PDF using Unstructured.

    Unstructured returns document elements, which are normalized into readable
    text while preserving element boundaries.
    """

    pdf = require_pdf(pdf_path)

    try:
        from unstructured.partition.pdf import partition_pdf
    except ModuleNotFoundError as exc:
        raise ParserError(
            "Python package 'unstructured' is not installed. "
            "Install it with: pip install unstructured[pdf]"
        ) from exc

    try:
        elements = partition_pdf(
            filename=str(pdf),
            strategy="fast",
        )
    except Exception as exc:
        raise ParserError(f"Unstructured failed to parse {pdf}: {exc}") from exc

    parts = []

    for element in elements:
        element_type = element.__class__.__name__
        text = str(element).strip()

        if not text:
            continue

        parts.append(f"[{element_type}]\n{text}")

    output_text = "\n\n".join(parts)

    return ParserResult(
        parser_name=PARSER_NAME,
        text=output_text,
        category=CATEGORY,
        output_format="text",
        metadata={
            "source_file": str(pdf),
            "element_count": len(elements),
            "strategy": "fast",
        },
        artifacts=[],
        raw=None,
    )