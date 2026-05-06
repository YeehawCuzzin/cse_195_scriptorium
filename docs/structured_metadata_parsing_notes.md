# Structured Metadata Parsing Notes

This document summarizes the current prototype for Issue #80: Structured Metadata Parsing.

## Goal

Issue #80 asks for a service that extracts:

- title
- authors
- abstract
- year
- DOI

from parsed document output, with a Crossref fallback if metadata is missing.

## Current Prototype

A lightweight prototype was added at:

- parsers/core/metadata.py

The prototype provides:

- extract_metadata(text, parser_name=None, crossref_fallback=False, mailto=None)
- extract_metadata_from_file(path, parser_name=None, crossref_fallback=False, mailto=None)

The returned object is a dictionary shaped like:

    {
        "title": str | None,
        "authors": list[str],
        "abstract": str | None,
        "year": int | None,
        "doi": str | None,
        "source": str,
        "parser_name": str | None
    }

## Current Approach

The prototype uses local heuristic extraction first:

- DOI regex detection
- year regex detection
- title detection from early non-noise lines
- author detection from lines near the title
- abstract extraction from text between Abstract and Introduction-like headings

Optional Crossref fallback is included through Python standard library requests using urllib.

## Current Limitations

This should be treated as a prototype, not the final backend service.

Known limitations:

- Author extraction is heuristic and may need GROBID TEI output for higher accuracy.
- The current benchmark stores normalized text, while structured GROBID XML/TEI would be better for production metadata extraction.
- Crossref fallback requires network access.
- This is not yet integrated into a backend UnifiedPaper schema.
- Strict unit tests still need to be added.

## Recommended Next Step

Use GROBID structured output as the primary source for academic metadata and use Crossref only as a fallback when DOI, title, year, or authors are missing.

Docling should remain the default parser candidate for readable document ingestion, while GROBID should be used as the companion metadata and bibliography parser.
