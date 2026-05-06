# Metadata & Bibliography Extraction Notes

This document summarizes the current status of metadata and bibliography extraction for the Scriptorium / RefAIned ingestion pipeline.

## Related Issue

- Issue #79: Implement Metadata & Bibliography Extraction

## Goal

The goal of this feature is to extract structured metadata and citation references from parsed academic documents so a UnifiedPaper model can be populated correctly and the graph database can receive citation/reference data.

## Current Status

This work is partially supported by the parser benchmark.

The benchmark includes GROBID, which is the strongest current parser candidate for scholarly metadata and bibliography extraction. GROBID is designed for academic documents and can support extraction of:

- title
- authors
- abstract
- publication metadata
- section structure
- references
- bibliography entries
- citation-related scholarly structure

The current parser benchmark successfully runs GROBID as part of the stable 9-parser benchmark.

## Current Evidence

The current repository includes:

- parsers/implementations/grobid_parser.py
- normalized GROBID text outputs under outputs/<pdf_name>/parser_outputs/grobid.txt
- parser status CSV files showing successful GROBID runs
- benchmark documentation identifying GROBID as the best candidate for scholarly metadata and reference extraction
- ADR-003 recommending GROBID as a companion parser for metadata and bibliography extraction

## Current Limitation

The current implementation does not yet fully populate a UnifiedPaper schema.

The current GROBID wrapper normalizes output into benchmark text files, but the next implementation step should preserve or parse structured GROBID output into explicit metadata fields.

## Proposed Structured Metadata Fields

A future UnifiedPaper or equivalent Pydantic schema should likely include:

    class UnifiedPaper:
        title: str | None
        authors: list[str]
        abstract: str | None
        year: int | None
        venue: str | None
        doi: str | None
        source_pdf_path: str
        parser_name: str
        references: list[Reference]

A Reference schema should likely include:

    class Reference:
        raw_text: str
        title: str | None
        authors: list[str]
        year: int | None
        venue: str | None
        doi: str | None

## Proposed Implementation Plan

### 1. Structured Metadata Parsing

Use GROBID output as the first metadata extraction source.

Initial fields to extract:

- title
- authors
- abstract
- DOI if available
- bibliography entries
- reference count

### 2. Bibliography Isolation & Citation Splitting

Separate bibliography/reference content from body text so it does not pollute semantic chunks.

Expected behavior:

- body text should be chunked for semantic retrieval
- bibliography entries should be stored separately
- references should be available for graph/citation workflows

### 3. Pydantic Schema Population

Create Pydantic models for parsed paper metadata and references.

Suggested files:

- parsers/core/schemas.py
- or backend-level schema files once the main API/database structure is finalized

### 4. Validation Tests

Future tests should use multiple academic PDF formats and assert:

- title is extracted correctly
- authors are extracted correctly
- abstract is detected
- bibliography is separated from body text
- reference count is reasonable
- parsed metadata can populate the target schema

## Suggested Validation Table

| PDF | Parser | Title Extracted | Authors Extracted | Abstract Extracted | References Extracted | Reference Count | Notes |
|---|---|---:|---:|---:|---:|---:|---|
| slam_llm.pdf | GROBID |  |  |  |  |  |  |
| cse195_research_paper.pdf | GROBID |  |  |  |  |  |  |
| cse188_research_paper.pdf | GROBID |  |  |  |  |  |  |

## Recommendation

Use GROBID as the first implementation target for metadata and bibliography extraction.

Recommended parser roles:

- Docling: default parser candidate for readable Markdown-style ingestion
- GROBID: companion parser for scholarly metadata, references, and bibliography extraction
- MinerU / Marker: artifact-rich parsing when figures, images, and layout artifacts matter

## Handoff Summary

This issue is not fully implemented yet, but the current parser benchmark provides the evidence and infrastructure needed to proceed.

Current contribution:

- GROBID is integrated into the parser benchmark.
- GROBID successfully runs in the JupyterHub environment.
- GROBID is identified as the preferred metadata/reference extraction candidate.
- The next step is to preserve structured GROBID output and map it into a formal schema.
