# Semantic Chunking & Golden Thread Notes

This document summarizes the current prototype for Issue #74: Implement Semantic Chunking & The Golden Thread.

## Goal

Issue #74 asks for raw parsed documents to be processed into structurally aware, embedding-ready chunks that retain source metadata for traceability.

## Current Prototype

A lightweight prototype was added at:

- parsers/core/chunking.py

The prototype includes:

- DocumentChunk dataclass
- chunk_markdown_text
- chunk_markdown_file
- write_chunks_jsonl

## DocumentChunk Fields

The current prototype chunk schema includes:

- chunk_id
- document_id
- text
- parser_name
- section_header
- chunk_index
- start_char
- end_char
- source_path

## Current Behavior

The prototype:

- reads Markdown or normalized parser text
- detects Markdown headings
- propagates the nearest section header into each chunk
- splits oversized sections by character length
- uses overlap for long chunks
- preserves parser name and source path metadata
- writes JSONL output suitable for later embedding experiments

## Example Use

    from parsers.core.chunking import chunk_markdown_file, write_chunks_jsonl

    chunks = chunk_markdown_file(
        "outputs/slam_llm/parser_outputs/docling.txt",
        document_id="slam_llm",
        parser_name="docling",
        max_chars=1200,
        overlap=200,
    )

    write_chunks_jsonl(
        chunks,
        "outputs/slam_llm/chunks/docling_chunks.jsonl",
    )

## Current Limitation

This is not a full Golden Thread implementation yet.

The current prototype preserves character offsets and parser/source metadata, but it does not yet preserve exact PDF page coordinates or bounding boxes. Exact PDF location metadata will require parser-specific layout output from tools such as Docling, MinerU, Marker, or GROBID.

## Recommended Next Steps

- Add strict tests with fake Markdown containing headers, tables, and equations.
- Ensure tables stay together in a single chunk.
- Add page number propagation when parser output provides page-level metadata.
- Add bounding box / PDF coordinate metadata when parser output supports it.
- Connect chunks to the future embedding pipeline.
- Store chunks in the eventual backend schema or vector database payload.
