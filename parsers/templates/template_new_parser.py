"""
Template for adding a new parser implementation.

Naming convention:
    parsers/implementations/<tool_name>_parser.py

Examples:
    parsers/implementations/docling_parser.py
    parsers/implementations/marker_parser.py
    parsers/implementations/nougat_parser.py
    parsers/implementations/uniparser_parser.py

Required public function:
    extract(pdf_path: str) -> ParserResult

After creating the parser file, add it to:
    parsers/core/registry.py
"""

from __future__ import annotations

from parsers.core.base import ParserError, ParserResult, require_pdf


PARSER_NAME = "new_parser_name"
CATEGORY = "structure_aware"  # flat_text | semi_structured | structure_aware | structured_metadata


def extract(pdf_path: str) -> ParserResult:
    """
    Parse a PDF and return a standardized ParserResult.

    Args:
        pdf_path:
            Path to the input PDF.

    Returns:
        ParserResult containing normalized text, metadata, artifacts, and optional raw output.
    """

    pdf = require_pdf(pdf_path)

    # Import optional parser dependencies inside this function.
    # This prevents one missing dependency from breaking the whole benchmark.
    try:
        # Example:
        # import some_parser_library
        pass
    except ModuleNotFoundError as exc:
        raise ParserError(
            "Missing dependency for this parser. Install with: pip install <package-name>"
        ) from exc

    # Run parser logic here.
    text = ""

    # Optional metadata/artifacts/raw output.
    metadata = {
        "source_file": str(pdf),
    }

    artifacts = []

    raw_output = None

    return ParserResult(
        parser_name=PARSER_NAME,
        text=text,
        category=CATEGORY,
        output_format="text",
        metadata=metadata,
        artifacts=artifacts,
        raw=raw_output,
    )