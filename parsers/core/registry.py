from __future__ import annotations

import importlib
from dataclasses import dataclass


@dataclass(frozen=True)
class ParserSpec:
    name: str
    module_name: str
    category: str
    requires: tuple[str, ...] = ()
    enabled: bool = True


PARSER_SPECS: dict[str, ParserSpec] = {
    "pymupdf": ParserSpec(
        name="pymupdf",
        module_name="pymupdf_parser",
        category="flat_text",
    ),
    "pdfplumber": ParserSpec(
        name="pdfplumber",
        module_name="pdfplumber_parser",
        category="flat_text",
    ),
    "pypdf": ParserSpec(
        name="pypdf",
        module_name="pypdf_parser",
        category="flat_text",
    ),
    "tika": ParserSpec(
        name="tika",
        module_name="tika_parser",
        category="semi_structured",
        requires=("tika", "java"),
    ),
    "unstructured": ParserSpec(
        name="unstructured",
        module_name="unstructured_parser",
        category="structure_aware",
        requires=("unstructured",),
    ),
    "mineru": ParserSpec(
        name="mineru",
        module_name="mineru_parser",
        category="structure_aware",
        requires=("mineru CLI",),
    ),
    "docling": ParserSpec(
        name="docling",
        module_name="docling_parser",
        category="structure_aware",
        requires=("docling",),
    ),
    "marker": ParserSpec(
        name="marker",
        module_name="marker_parser",
        category="structure_aware",
        requires=("marker-pdf",),
    ),
    "grobid": ParserSpec(
        name="grobid",
        module_name="grobid_parser",
        category="structured_metadata",
        requires=("GROBID server at localhost:8070",),
    ),
}


def load_parsers(selected: list[str] | None = None):
    """
    Safely import parser implementation modules.
    """

    if selected:
        unknown = [name for name in selected if name not in PARSER_SPECS]
        if unknown:
            print(f"Warning: unknown parser names ignored: {unknown}")

        specs = {
            name: PARSER_SPECS[name]
            for name in selected
            if name in PARSER_SPECS
        }
    else:
        specs = PARSER_SPECS

    loaded = {}
    import_errors = {}

    for name, spec in specs.items():
        if not spec.enabled:
            continue

        try:
            module = importlib.import_module(
                f"parsers.implementations.{spec.module_name}"
            )

            loaded[name] = {
                "module": module,
                "spec": spec,
            }

        except Exception as exc:
            import_errors[name] = repr(exc)

    return loaded, import_errors