from __future__ import annotations

import os
import shutil
from pathlib import Path

from parsers.core.base import ParserError, ParserResult, require_pdf


PARSER_NAME = "docling"
CATEGORY = "structure_aware"


def extract(pdf_path: str) -> ParserResult:
    """
    Extract structured Markdown from a PDF using Docling.

    Docling is a structure-aware parser that converts PDFs into a rich
    DoclingDocument representation and can export to Markdown.
    """

    pdf = require_pdf(pdf_path)

    try:
        from docling.document_converter import DocumentConverter
    except ModuleNotFoundError as exc:
        raise ParserError(
            "Python package 'docling' is not installed. Install it with: pip install docling"
        ) from exc

    parser_output_dir = Path(
        os.environ.get(
            "SCRIPTORIUM_PARSER_OUTPUT_DIR",
            str(Path("outputs") / pdf.stem / "parser_outputs"),
        )
    )

    output_root = parser_output_dir / "docling_run"

    if output_root.exists():
        shutil.rmtree(output_root)

    output_root.mkdir(parents=True, exist_ok=True)

    try:
        converter = DocumentConverter()
        result = converter.convert(str(pdf))
        markdown = result.document.export_to_markdown()

    except Exception as exc:
        raise ParserError(f"Docling failed to convert {pdf}: {exc}") from exc

    markdown_path = output_root / f"{pdf.stem}.md"
    markdown_path.write_text(markdown, encoding="utf-8", errors="ignore")

    artifacts = [str(markdown_path)]

    return ParserResult(
        parser_name=PARSER_NAME,
        text=markdown,
        category=CATEGORY,
        output_format="markdown",
        metadata={
            "source_file": str(pdf),
            "output_root": str(output_root),
            "selected_output": str(markdown_path),
            "artifact_count": len(artifacts),
        },
        artifacts=artifacts,
        raw=None,
    )