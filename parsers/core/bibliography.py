from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class BibliographySplitResult:
    body_text: str
    bibliography_text: str | None
    citations: list[str]
    reference_count: int
    source_path: str | None = None
    parser_name: str | None = None


_REFERENCES_HEADING_RE = re.compile(
    r"(?im)^\s*(#{1,6}\s*)?(references|bibliography|works cited|literature cited)\s*$"
)

_NUMBERED_CITATION_RE = re.compile(
    r"(?m)(?=^\s*(?:\[\d+\]|\d+\.|\d+\))\s+)"
)


def _clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _clean_citation(citation: str) -> str:
    citation = citation.strip()
    citation = re.sub(r"\s+", " ", citation)
    citation = re.sub(r"^\s*(?:\[\d+\]|\d+\.|\d+\))\s*", "", citation)
    return citation.strip()


def find_bibliography_start(text: str) -> int | None:
    match = None

    for candidate in _REFERENCES_HEADING_RE.finditer(text):
        match = candidate

    if match is None:
        return None

    return match.start()


def split_body_and_bibliography(text: str) -> tuple[str, str | None]:
    cleaned = _clean_text(text)
    start = find_bibliography_start(cleaned)

    if start is None:
        return cleaned, None

    body = cleaned[:start].strip()
    bibliography = cleaned[start:].strip()

    return body, bibliography


def split_citations(bibliography_text: str | None) -> list[str]:
    if not bibliography_text:
        return []

    text = _clean_text(bibliography_text)

    lines = text.splitlines()

    if lines and re.match(r"^\s*(#{1,6}\s*)?(references|bibliography|works cited|literature cited)\s*$", lines[0], re.IGNORECASE):
        text = "\n".join(lines[1:]).strip()

    if not text:
        return []

    parts = _NUMBERED_CITATION_RE.split(text)

    citations = []

    if len(parts) > 1:
        for part in parts:
            cleaned = _clean_citation(part)
            if len(cleaned) >= 20:
                citations.append(cleaned)
    else:
        paragraph_parts = re.split(r"\n\s*\n", text)

        for part in paragraph_parts:
            cleaned = _clean_citation(part)
            if len(cleaned) >= 20:
                citations.append(cleaned)

    return citations


def isolate_bibliography_and_citations(
    text: str,
    source_path: str | None = None,
    parser_name: str | None = None,
) -> dict:
    body_text, bibliography_text = split_body_and_bibliography(text)
    citations = split_citations(bibliography_text)

    result = BibliographySplitResult(
        body_text=body_text,
        bibliography_text=bibliography_text,
        citations=citations,
        reference_count=len(citations),
        source_path=source_path,
        parser_name=parser_name,
    )

    return asdict(result)


def isolate_bibliography_from_file(
    path: str | Path,
    parser_name: str | None = None,
) -> dict:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8", errors="ignore")

    return isolate_bibliography_and_citations(
        text=text,
        source_path=str(file_path),
        parser_name=parser_name,
    )
