from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from parsers.core.base import ParserError, ParserResult, require_pdf


PARSER_NAME = "marker"
CATEGORY = "structure_aware"


def _select_best_output(output_root: Path, pdf_stem: str) -> Path:
    preferred_names = [
        f"{pdf_stem}.md",
        "output.md",
        "markdown.md",
    ]

    for name in preferred_names:
        matches = list(output_root.rglob(name))
        if matches:
            return matches[0]

    candidate_files: list[Path] = []
    candidate_files.extend(output_root.rglob("*.md"))
    candidate_files.extend(output_root.rglob("*.txt"))
    candidate_files.extend(output_root.rglob("*.json"))
    candidate_files.extend(output_root.rglob("*.html"))

    if not candidate_files:
        raise ParserError(
            f"Marker completed, but no .md/.txt/.json/.html output was found in {output_root}"
        )

    suffix_priority = {
        ".md": 0,
        ".txt": 1,
        ".json": 2,
        ".html": 3,
    }

    candidate_files.sort(
        key=lambda path: (
            suffix_priority.get(path.suffix.lower(), 99),
            len(str(path)),
        )
    )

    return candidate_files[0]


def extract(pdf_path: str) -> ParserResult:
    """
    Extract structured Markdown from a PDF using Marker.

    Uses marker_single CLI from marker-pdf.
    """

    pdf = require_pdf(pdf_path)

    marker_exe = shutil.which("marker_single")
    if marker_exe is None:
        raise ParserError(
            "Marker CLI 'marker_single' was not found in PATH. "
            "Install it with: pip install -U marker-pdf"
        )

    parser_output_dir = Path(
        os.environ.get(
            "SCRIPTORIUM_PARSER_OUTPUT_DIR",
            str(Path("outputs") / pdf.stem / "parser_outputs"),
        )
    )

    output_root = parser_output_dir / "marker_run"

    if output_root.exists():
        shutil.rmtree(output_root)

    output_root.mkdir(parents=True, exist_ok=True)

    cmd = [
        marker_exe,
        str(pdf),
        "--output_dir",
        str(output_root),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise ParserError(
            "Marker failed.\n"
            f"Command:\n{' '.join(cmd)}\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )

    best_output = _select_best_output(output_root, pdf.stem)
    text = best_output.read_text(encoding="utf-8", errors="ignore")

    artifacts = [
        str(path)
        for path in output_root.rglob("*")
        if path.is_file()
    ]

    return ParserResult(
        parser_name=PARSER_NAME,
        text=text,
        category=CATEGORY,
        output_format=best_output.suffix.lstrip(".") or "text",
        metadata={
            "source_file": str(pdf),
            "output_root": str(output_root),
            "selected_output": str(best_output),
            "artifact_count": len(artifacts),
            "command": " ".join(cmd),
        },
        artifacts=artifacts,
        raw={
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        },
    )
