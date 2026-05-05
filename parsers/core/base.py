from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


ParserCategory = Literal[
    "flat_text",
    "semi_structured",
    "structure_aware",
    "structured_metadata",
]


@dataclass
class ParserResult:
    """Standard output object returned by every parser wrapper."""

    parser_name: str
    text: str
    category: ParserCategory
    output_format: str = "text"
    metadata: dict[str, Any] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    raw: Any | None = None

    @property
    def chars(self) -> int:
        return len(self.text or "")


class ParserError(RuntimeError):
    """Raised when a parser dependency or runtime requirement fails."""


def require_pdf(pdf_path: str | Path) -> Path:
    """Validate that the input path exists and points to a PDF file."""

    pdf = Path(pdf_path)

    if not pdf.exists():
        raise FileNotFoundError(f"PDF not found: {pdf}")

    if pdf.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {pdf}")

    return pdf


def normalize_to_text(result: Any) -> str:
    """
    Convert parser outputs into plain text for chunking/retrieval.

    Supports:
    - ParserResult
    - str
    - list[dict] from older Unstructured-style parser output
    - dict from older GROBID-style structured output
    """

    if isinstance(result, ParserResult):
        return result.text

    if isinstance(result, str):
        return result

    if isinstance(result, list):
        parts: list[str] = []

        for item in result:
            if isinstance(item, dict):
                label = item.get("type", "Element")
                text = item.get("text", "")

                if text:
                    parts.append(f"[{label}]\n{text}")
            else:
                parts.append(str(item))

        return "\n\n".join(parts)

    if isinstance(result, dict):
        parts: list[str] = []

        if result.get("title"):
            parts.append(f"# {result['title']}")

        if result.get("authors"):
            parts.append("Authors: " + ", ".join(result["authors"]))

        if result.get("abstract"):
            parts.append("## Abstract\n" + result["abstract"])

        for section in result.get("sections", []):
            heading = section.get("heading", "")
            text = section.get("text", "")

            if heading:
                parts.append(f"## {heading}\n{text}")
            elif text:
                parts.append(text)

        if result.get("references"):
            refs = []

            for ref in result["references"]:
                refs.append(ref.get("title") or ref.get("raw", ""))

            parts.append("## References\n" + "\n".join(refs))

        return "\n\n".join(parts)

    return str(result)