# ADR-003: PDF Parsing Engine Selection

## Status

Proposed

## Date

2026-05-05

## Context

Scriptorium / RefAIned needs a reliable document parsing and ingestion baseline for research-focused retrieval-augmented generation (RAG). Academic PDFs are difficult to process because they often contain multi-column layouts, section hierarchies, tables, figures, equations, references, and metadata.

Parser choice affects downstream chunking, embedding quality, retrieval coherence, citation traceability, and source-aware reasoning. A parser that only extracts raw text may be fast, but it may lose the structure needed for semantic chunking and Golden Thread traceability. A structure-aware parser may produce better outputs, but it may introduce runtime cost, dependency complexity, or service requirements.

This ADR summarizes the parser benchmark results and recommends a default PDF parsing direction for the ingestion engine.

## Decision Drivers

The parser selection should balance:

- Extraction fidelity
- Structure preservation
- Metadata and bibliography integrity
- Runtime performance
- Operational simplicity
- Local hostability
- Maintainability in the JupyterHub / lab server environment
- Suitability for downstream chunking, retrieval, and traceability

## Options Considered

### PyMuPDF

Fast flat-text baseline. Easy to run and useful for quick extraction, but limited structural preservation.

### pdfplumber

Flat-text baseline with some layout sensitivity. Useful for comparison, but can produce noisy output on multi-column academic PDFs.

### PyPDF

Fast general-purpose PDF text extraction baseline. Limited structural awareness.

### Apache Tika

Semi-structured Java-based document extraction. Fast once Java is available, but does not preserve rich academic structure or artifacts.

### Unstructured

Structure-aware parser that provides more document element awareness than flat text extraction. Useful for downstream chunking experiments.

### Docling

Structure-aware parser with strong Markdown-oriented output. Good balance between runtime and structural preservation.

### Marker

Structure-aware parser that produces rich Markdown and image artifacts. Useful when artifact generation is important, but slower than Docling.

### MinerU

Layout-aware parser that produces Markdown, JSON, image assets, layout PDFs, and other artifacts. Strong for multimodal-ready ingestion, but has higher setup and runtime complexity.

### GROBID

Scholarly document parser focused on academic metadata, authors, references, bibliography, and structured scholarly text. Requires a running service at `localhost:8070`.

## Benchmark Summary

The stable benchmark ran nine parsers successfully against the main test PDF.

| Parser | Characters | Runtime (s) | Type |
|---|---:|---:|---|
| PyMuPDF | 88,199 | 0.09 | Flat text |
| pdfplumber | 85,465 | 1.74 | Flat text |
| PyPDF | 88,394 | 0.54 | Flat text |
| Tika | 90,660 | 0.09 | Semi-structured |
| Unstructured | 95,836 | 4.56 | Structure-aware |
| Docling | 100,840 | 10.34 | Structure-aware |
| Marker | 102,133 | 40.50 | Structure-aware |
| MinerU | 88,200 | 31.92 | Structure-aware |
| GROBID | 69,846 | 2.02 | Structured metadata |

## Decision

Use **Docling as the recommended default parser candidate** for general document ingestion because it provides the best balance of structure preservation, readable Markdown output, local execution, and runtime performance.

Use **GROBID as a companion parser for scholarly metadata and bibliography extraction**, especially when title, authors, references, and citation structure are important.

Keep **PyMuPDF, PyPDF, pdfplumber, and Tika as fast baseline parsers** for comparison, debugging, and fallback extraction.

Keep **Marker and MinerU as artifact-rich parser candidates** for cases where richer Markdown, extracted images, layout PDFs, JSON artifacts, or multimodal-ready outputs are more important than runtime cost.

## Consequences

### Positive Consequences

- The ingestion engine has a clear default parser direction instead of relying on ad hoc parser choice.
- Docling provides structure-aware Markdown output suitable for future semantic chunking work.
- GROBID supports academic metadata and bibliography extraction.
- The benchmark remains reproducible because all parser outputs are saved under `outputs/<pdf_name>/parser_outputs/`.
- The framework can still compare multiple parsers through the shared parser registry and `extract(pdf_path)` interface.

### Negative Consequences

- Docling may not preserve every table, figure, or equation as richly as MinerU or Marker.
- GROBID requires a running Java service.
- MinerU and Marker remain useful but are slower and more operationally complex.
- The current decision is based on a small benchmark set and should be revisited after chunking and retrieval evaluation.

### Neutral / Follow-up Consequences

- Parser selection should be revisited after evaluating chunk quality, retrieval top-k quality, citation preservation, and Golden Thread traceability.
- Future work should add automated scoring for table preservation, equation handling, section hierarchy, and metadata integrity.
- Dependency-sensitive parsers such as Nougat and PaddleOCR may require isolated environments before they can be reconsidered.

## Related Artifacts

Repository:

- https://github.com/YeehawCuzzin/cse_195_scriptorium

JupyterHub:

- https://jupyter.csed.io/user/yeehawcuzzin/lab

Relevant files:

- `scriptorium.ipynb`
- `run_all_input_pdfs.ipynb`
- `docs/parser_evaluation_metrics.md`
- `docs/parser_visual_quantitative_audit.md`
- `outputs/slam_llm/parser_status.csv`
- `outputs/slam_llm/parser_outputs/`

## Review Status

This ADR is proposed for PI / mentor review. The recommendation should be treated as an ingestion baseline, not a final permanent parser decision.
