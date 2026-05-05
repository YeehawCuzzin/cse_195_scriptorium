from __future__ import annotations

import os
import time
from pathlib import Path

from parsers.core.base import normalize_to_text
from parsers.core.registry import PARSER_SPECS, load_parsers


def run_parsers(
    pdf_path: str | Path,
    output_dir: str | Path = "outputs/parser_outputs",
    selected: list[str] | None = None,
):
    """
    Run available parsers and save normalized text outputs.

    Args:
        pdf_path:
            Path to the input PDF.

        output_dir:
            Directory where normalized parser text outputs will be saved.

        selected:
            Optional list of parser names to run.
            Example: ["pymupdf", "pdfplumber", "unstructured"]

    Returns:
        parser_outputs:
            dict[str, str] mapping parser name to normalized text output.

        parser_status:
            list[dict] containing status/error/runtime info for each parser.
    """

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    loaded, import_errors = load_parsers(selected=selected)

    parser_outputs: dict[str, str] = {}
    parser_status: list[dict] = []

    # Let parser implementations know where this run's parser output folder is.
    # Example:
    # outputs/slam_llm/parser_outputs/
    old_parser_output_dir = os.environ.get("SCRIPTORIUM_PARSER_OUTPUT_DIR")
    os.environ["SCRIPTORIUM_PARSER_OUTPUT_DIR"] = str(output_dir)

    try:
        for parser_name, info in loaded.items():
            module = info["module"]
            spec = info["spec"]

            start_time = time.perf_counter()

            try:
                raw_result = module.extract(str(pdf_path))
                elapsed = time.perf_counter() - start_time

                normalized_text = normalize_to_text(raw_result)
                parser_outputs[parser_name] = normalized_text

                out_path = output_dir / f"{parser_name}.txt"
                out_path.write_text(
                    normalized_text,
                    encoding="utf-8",
                    errors="ignore",
                )

                parser_status.append(
                    {
                        "parser": parser_name,
                        "status": "success",
                        "chars": len(normalized_text),
                        "runtime_seconds": round(elapsed, 2),
                        "type": spec.category,
                        "requires": ", ".join(spec.requires),
                        "error": "",
                        "output_path": str(out_path),
                    }
                )

            except Exception as exc:
                elapsed = time.perf_counter() - start_time

                parser_status.append(
                    {
                        "parser": parser_name,
                        "status": "failed",
                        "chars": 0,
                        "runtime_seconds": round(elapsed, 2),
                        "type": spec.category,
                        "requires": ", ".join(spec.requires),
                        "error": repr(exc),
                        "output_path": "",
                    }
                )

        for parser_name, error in import_errors.items():
            spec = PARSER_SPECS.get(parser_name)

            parser_status.append(
                {
                    "parser": parser_name,
                    "status": "import_failed",
                    "chars": 0,
                    "runtime_seconds": 0,
                    "type": spec.category if spec else "",
                    "requires": ", ".join(spec.requires) if spec else "",
                    "error": error,
                    "output_path": "",
                }
            )

    finally:
        # Restore previous environment variable state so repeated notebook runs
        # do not leak stale output paths.
        if old_parser_output_dir is None:
            os.environ.pop("SCRIPTORIUM_PARSER_OUTPUT_DIR", None)
        else:
            os.environ["SCRIPTORIUM_PARSER_OUTPUT_DIR"] = old_parser_output_dir

    return parser_outputs, parser_status