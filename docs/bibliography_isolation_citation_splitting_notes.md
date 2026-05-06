# Bibliography Isolation & Citation Splitting Notes

This document summarizes the current prototype for Issue #81: Bibliography Isolation & Citation Splitting.

## Goal

Issue #81 asks for a function that detects the References or Bibliography section, removes it from the main text, and splits the bibliography into individual citation strings.

## Current Prototype

A lightweight prototype was added at:

- parsers/core/bibliography.py

The prototype includes:

- find_bibliography_start
- split_body_and_bibliography
- split_citations
- isolate_bibliography_and_citations
- isolate_bibliography_from_file

## Returned Shape

The main function returns a dictionary with:

- body_text
- bibliography_text
- citations
- reference_count
- source_path
- parser_name

## Current Behavior

The prototype:

- detects headings such as References, Bibliography, Works Cited, and Literature Cited
- separates body text from bibliography text
- splits numbered citations using patterns such as [1], 1., and 1)
- falls back to paragraph splitting when numbered citation markers are not found
- returns a clean list of citation strings
- preserves parser name and source path metadata

## Example Use

    from parsers.core.bibliography import isolate_bibliography_from_file

    result = isolate_bibliography_from_file(
        "outputs/slam_llm/parser_outputs/grobid.txt",
        parser_name="grobid",
    )

    print(result["reference_count"])
    print(result["citations"][:3])

## Current Limitations

This should be treated as a prototype, not the final production citation service.

Known limitations:

- Some parser outputs may flatten or alter reference formatting.
- GROBID structured TEI/XML output would likely be more reliable than normalized text for production citation extraction.
- The splitter currently focuses on reference-section isolation, not inline citation matching.
- Strict unit tests still need to be added across multiple journal formats.
- Graph database integration is not implemented here.

## Recommended Next Steps

- Preserve structured GROBID output and parse references from TEI/XML when possible.
- Add unit tests for IEEE-style, APA-like, and unnumbered bibliography formats.
- Return structured Reference objects after schema decisions are finalized.
- Connect citation output to the graph database citation pipeline.
- Avoid including bibliography text in semantic body chunks unless explicitly requested.
