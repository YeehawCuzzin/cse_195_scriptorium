from __future__ import annotations

import shutil

from parsers.core.base import ParserError, ParserResult, require_pdf


PARSER_NAME = "tika"
CATEGORY = "semi_structured"


def extract(pdf_path: str) -> ParserResult:
    """
    Extract PDF text using Apache Tika.

    Tika requires:
    - Python package: tika
    - Java available in PATH

    The old parser directly imported `from tika import parser` at the top level.
    This version imports Tika inside extract() so a missing Tika dependency does
    not break the entire parser registry.
    """

    pdf = require_pdf(pdf_path)

    if shutil.which("java") is None:
        raise ParserError(
            "Java was not found in PATH. Apache Tika requires Java to start "
            "the Tika server."
        )

    try:
        from tika import parser
    except ModuleNotFoundError as exc:
        raise ParserError(
            "Python package 'tika' is not installed. Install it with: pip install tika"
        ) from exc

    parsed = parser.from_file(str(pdf))

    content = parsed.get("content", "") or ""
    metadata = parsed.get("metadata", {}) or {}

    return ParserResult(
        parser_name=PARSER_NAME,
        text=content,
        category=CATEGORY,
        output_format="text",
        metadata={
            "source_file": str(pdf),
            "tika_metadata": metadata,
        },
        artifacts=[],
        raw=parsed,
    )