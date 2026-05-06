from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class DocumentChunk:
    chunk_id: str
    document_id: str
    text: str
    parser_name: str | None
    section_header: str | None
    chunk_index: int
    start_char: int
    end_char: int
    source_path: str | None = None


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def _normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_markdown_blocks(text: str) -> list[tuple[str | None, str]]:
    blocks: list[tuple[str | None, str]] = []
    current_header: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        heading_match = _HEADING_RE.match(line.strip())

        if heading_match:
            if current_lines:
                blocks.append((current_header, "\n".join(current_lines).strip()))
                current_lines = []

            current_header = heading_match.group(2).strip()
            current_lines.append(line)
        else:
            current_lines.append(line)

    if current_lines:
        blocks.append((current_header, "\n".join(current_lines).strip()))

    return [(header, block) for header, block in blocks if block]


def _split_large_block(block: str, max_chars: int, overlap: int) -> list[str]:
    if len(block) <= max_chars:
        return [block]

    chunks = []
    start = 0

    while start < len(block):
        end = min(start + max_chars, len(block))
        window = block[start:end]

        if end < len(block):
            split_candidates = [
                window.rfind("\n\n"),
                window.rfind(". "),
                window.rfind("\n"),
            ]
            split_at = max(split_candidates)

            if split_at > max_chars * 0.5:
                end = start + split_at + 1
                window = block[start:end]

        chunks.append(window.strip())

        if end >= len(block):
            break

        start = max(0, end - overlap)

    return [chunk for chunk in chunks if chunk]


def chunk_markdown_text(
    text: str,
    document_id: str,
    parser_name: str | None = None,
    source_path: str | None = None,
    max_chars: int = 1200,
    overlap: int = 200,
) -> list[DocumentChunk]:
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= max_chars:
        raise ValueError("overlap must be smaller than max_chars")

    normalized = _normalize_text(text)
    blocks = _split_markdown_blocks(normalized)

    chunks: list[DocumentChunk] = []
    search_start = 0

    for section_header, block in blocks:
        pieces = _split_large_block(block, max_chars=max_chars, overlap=overlap)

        for piece in pieces:
            start_char = normalized.find(piece[:80], search_start)

            if start_char == -1:
                start_char = search_start

            end_char = start_char + len(piece)
            chunk_index = len(chunks)

            chunks.append(
                DocumentChunk(
                    chunk_id=f"{document_id}::chunk_{chunk_index:04d}",
                    document_id=document_id,
                    text=piece,
                    parser_name=parser_name,
                    section_header=section_header,
                    chunk_index=chunk_index,
                    start_char=start_char,
                    end_char=end_char,
                    source_path=source_path,
                )
            )

            search_start = max(search_start, end_char)

    return chunks


def chunk_markdown_file(
    path: str | Path,
    document_id: str | None = None,
    parser_name: str | None = None,
    max_chars: int = 1200,
    overlap: int = 200,
) -> list[dict]:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8", errors="ignore")

    if document_id is None:
        document_id = file_path.stem

    chunks = chunk_markdown_text(
        text=text,
        document_id=document_id,
        parser_name=parser_name,
        source_path=str(file_path),
        max_chars=max_chars,
        overlap=overlap,
    )

    return [asdict(chunk) for chunk in chunks]


def write_chunks_jsonl(chunks: list[dict], output_path: str | Path) -> Path:
    import json

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    return path
