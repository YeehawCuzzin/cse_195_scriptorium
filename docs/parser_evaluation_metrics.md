# Parser Evaluation Metrics

This document defines an initial scoring rubric for evaluating PDF parsers in the Scriptorium / RefAIned ingestion pipeline.

The goal is to compare parser outputs in a way that supports parser selection, ingestion design, semantic chunking, citation traceability, and downstream RAG quality.

## Scoring Scale

Each qualitative metric is scored from 0 to 3.

| Score | Meaning |
|---:|---|
| 0 | Fails or unusable |
| 1 | Poor / major issues |
| 2 | Usable / minor issues |
| 3 | Strong / reliable |

## Evaluation Categories

### 1. Text Extraction Quality

Measures whether the parser extracts readable and complete text.

| Score | Description |
|---:|---|
| 0 | Missing most text or extraction fails |
| 1 | Major corruption, merged words, broken reading order, or severe noise |
| 2 | Mostly readable with some spacing, header/footer, or ordering issues |
| 3 | Clean readable text with minimal noise |

### 2. Hierarchy Detection

Measures whether the parser preserves document structure such as title, abstract, headings, sections, and subsections.

| Score | Description |
|---:|---|
| 0 | No useful hierarchy preserved |
| 1 | Some headings appear, but structure is inconsistent or flattened |
| 2 | Main headings/sections are mostly preserved |
| 3 | Clear hierarchy suitable for section-aware chunking |

### 3. Table Preservation

Measures whether tables remain understandable and useful after parsing.

| Score | Description |
|---:|---|
| 0 | Tables missing or completely unreadable |
| 1 | Table text extracted but structure is mostly lost |
| 2 | Table structure is partially preserved or recoverable |
| 3 | Tables are preserved in a clearly structured format or artifact |

### 4. Figure and Caption Preservation

Measures whether figures, captions, and image references are retained.

| Score | Description |
|---:|---|
| 0 | Figures/captions missing |
| 1 | Captions appear but are disconnected from figures |
| 2 | Captions and figure references are mostly preserved |
| 3 | Figures/captions are preserved with usable references or extracted artifacts |

### 5. Equation / Math Handling

Measures whether equations and math-heavy content remain usable.

| Score | Description |
|---:|---|
| 0 | Equations missing or unreadable |
| 1 | Math symbols mostly corrupted or flattened |
| 2 | Equations partially readable but not structurally preserved |
| 3 | Equations are readable and preserve meaningful formatting |

### 6. Metadata and Bibliography Integrity

Measures whether title, authors, DOI, references, bibliography, and citation structure are preserved.

| Score | Description |
|---:|---|
| 0 | Metadata/references missing or unusable |
| 1 | Some metadata appears but is noisy or mixed into body text |
| 2 | Most metadata/references are recoverable |
| 3 | Metadata and bibliography are clearly structured and useful |

### 7. Runtime Performance

Measures parser runtime on the benchmark document.

| Score | Description |
|---:|---|
| 0 | Fails or impractically slow |
| 1 | Slow; major runtime cost |
| 2 | Moderate runtime |
| 3 | Fast runtime |

Suggested thresholds for the current small benchmark:

| Score | Runtime |
|---:|---|
| 3 | Under 2 seconds |
| 2 | 2 to 15 seconds |
| 1 | 15 to 60 seconds |
| 0 | Over 60 seconds or failed |

### 8. Operational Complexity

Measures setup difficulty, dependency conflicts, and maintainability.

| Score | Description |
|---:|---|
| 0 | Not viable in shared environment |
| 1 | Heavy setup, fragile dependencies, or service complexity |
| 2 | Some setup required but maintainable |
| 3 | Simple install/use and easy to maintain |

## Blank Benchmark Results Table

Use this table when evaluating parser outputs against a ground truth PDF.

| Parser | Text Quality | Hierarchy | Tables | Figures/Captions | Equations/Math | Metadata/Bibliography | Runtime | Operational Complexity | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| PyMuPDF |  |  |  |  |  |  |  |  |  |
| pdfplumber |  |  |  |  |  |  |  |  |  |
| PyPDF |  |  |  |  |  |  |  |  |  |
| Tika |  |  |  |  |  |  |  |  |  |
| Unstructured |  |  |  |  |  |  |  |  |  |
| Docling |  |  |  |  |  |  |  |  |  |
| Marker |  |  |  |  |  |  |  |  |  |
| MinerU |  |  |  |  |  |  |  |  |  |
| GROBID |  |  |  |  |  |  |  |  |  |

## Current Quantitative Metrics Already Captured

The current benchmark already records:

- Parser success/failure status
- Extracted character count
- Runtime in seconds
- Parser category/type
- Requirements/dependencies
- Error messages if failed
- Output path
- Output inventory
- Qualitative output previews

## Future Metrics

Future benchmark iterations should add:

- Chunk count per parser
- Average chunk length
- Section-aware chunk boundary quality
- Table retention after chunking
- Reference/citation preservation after chunking
- Retrieval top-k quality
- Human-rated relevance and coherence
- Source traceability / Golden Thread integrity
