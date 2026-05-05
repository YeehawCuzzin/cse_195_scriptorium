# CSE 195 Scriptorium Parser Benchmark

This repository contains the parser benchmark work for the CSE 195 Scriptorium / RefAIned project. The goal is to evaluate and compare PDF parsing strategies for research-focused retrieval-augmented generation (RAG) pipelines.

## Project Summary

The benchmark tests multiple PDF parsers on scientific/research PDFs and saves normalized outputs for comparison. The current stable benchmark runs 9 local parsers successfully:

- PyMuPDF
- pdfplumber
- PyPDF
- Apache Tika
- Unstructured
- Docling
- Marker
- MinerU
- GROBID

The benchmark records:

- Parser success/failure status
- Extracted character count
- Runtime
- Output file paths
- Normalized `.txt` parser outputs
- Parser-specific artifact folders when available

## JupyterHub Environment

This project was developed and tested in the CSED JupyterHub environment:

https://jupyter.csed.io/user/yeehawcuzzin

## Repository Structure

    .
    ├── inputs/
    │   ├── slam_llm.pdf
    │   ├── cse188_research_paper.pdf
    │   └── cse195_research_paper.pdf
    │
    ├── outputs/
    │   ├── slam_llm/
    │   ├── cse188_research_paper/
    │   ├── cse195_research_paper/
    │   └── combined_parser_status.csv
    │
    ├── parsers/
    │   ├── core/
    │   │   ├── base.py
    │   │   ├── registry.py
    │   │   └── runner.py
    │   │
    │   ├── implementations/
    │   │   ├── pymupdf_parser.py
    │   │   ├── pdfplumber_parser.py
    │   │   ├── pypdf_parser.py
    │   │   ├── tika_parser.py
    │   │   ├── unstructured_parser.py
    │   │   ├── docling_parser.py
    │   │   ├── marker_parser.py
    │   │   ├── mineru_parser.py
    │   │   └── grobid_parser.py
    │   │
    │   └── templates/
    │       └── template_new_parser.py
    │
    ├── scriptorium.ipynb
    ├── run_all_input_pdfs.ipynb
    ├── README.md
    └── .gitignore

## Main Notebooks

### `scriptorium.ipynb`

Clean findings notebook showing the parser benchmark work, including:

- Benchmark scope
- Parser framework check
- GROBID setup instructions
- 9-parser benchmark run
- Runtime comparison
- Character count comparison
- Output previews
- Findings and excluded parser notes

### `run_all_input_pdfs.ipynb`

Batch runner notebook that runs the 9-parser benchmark across PDFs located in the `inputs/` folder.

## Parser Framework

The parser framework is organized around a shared interface.

Each parser implementation exposes:

    extract(pdf_path)

and returns a standardized `ParserResult`.

Core files:

- `parsers/core/base.py`: shared result types and validation helpers
- `parsers/core/registry.py`: parser registry and metadata
- `parsers/core/runner.py`: benchmark execution and output writing
- `parsers/implementations/`: parser-specific wrappers

## GROBID Requirement

GROBID must be running before the GROBID parser can be used.

In a JupyterHub terminal, run:

    cd /home/jovyan/grobid-0.9.0
    export JAVA_HOME=/opt/conda
    export PATH=$JAVA_HOME/bin:$PATH
    ./gradlew :grobid-service:run

Leave that terminal running while executing the benchmark.

The benchmark checks GROBID at:

    http://localhost:8070/api/isalive

Expected response:

    true

## Running the Benchmark

Open `scriptorium.ipynb` or `run_all_input_pdfs.ipynb` in JupyterHub.

For the stable 9-parser benchmark, the selected parsers are:

    SELECTED_PARSERS = [
        "pymupdf",
        "pdfplumber",
        "pypdf",
        "tika",
        "unstructured",
        "docling",
        "marker",
        "mineru",
        "grobid",
    ]

Outputs are saved under:

    outputs/<pdf_name>/parser_outputs/

Each run also creates:

    outputs/<pdf_name>/parser_status.csv

The batch runner also creates:

    outputs/combined_parser_status.csv

## Excluded Parsers

Some parsers were explored but excluded from the final stable benchmark:

- **Nougat**: worked separately, but required older dependency pins that conflicted with the modern parser stack.
- **PaddleOCR**: installed and downloaded model files, but failed during runtime inference in the JupyterHub environment.
- **Uni-Parser / Uniparser**: the originally linked project was not a PDF parser, and the document-focused version did not have a simple local integration path.
- **PyMuPDF4LLM**: excluded because it overlapped heavily with PyMuPDF and did not add a distinct parser category.

## Current Stable Result

The final stable benchmark achieves a 9/9 parser run on the main test PDF.

The benchmark demonstrates tradeoffs between:

- speed
- structure preservation
- artifact generation
- runtime complexity
- dependency management
- scholarly metadata extraction

## Future Work

Next steps include:

- Chunking each parser output consistently
- Measuring chunk counts and average chunk length
- Running embedding-based retrieval
- Comparing top-k retrieval quality
- Evaluating section, table, caption, reference, and figure preservation
- Exploring isolated environments for dependency-sensitive parsers
