from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from parsers.core.base import ParserError, ParserResult, require_pdf


PARSER_NAME = "mineru"
CATEGORY = "structure_aware"


def _flatten_mineru_output(output_root: Path, pdf_stem: str) -> Path:
    """
    MinerU normally creates:
        output_root/<pdf_stem>/txt/<files>

    This function moves those files up to:
        output_root/<files>

    Then it removes the extra nested <pdf_stem>/ directory.
    """

    nested_txt_dir = output_root / pdf_stem / "txt"

    if not nested_txt_dir.exists():
        return output_root

    for item in nested_txt_dir.iterdir():
        destination = output_root / item.name

        if destination.exists():
            if destination.is_dir():
                shutil.rmtree(destination)
            else:
                destination.unlink()

        shutil.move(str(item), str(destination))

    nested_pdf_dir = output_root / pdf_stem
    if nested_pdf_dir.exists():
        shutil.rmtree(nested_pdf_dir)

    return output_root


def _select_best_text_output(output_root: Path, pdf_stem: str) -> Path:
    """
    Prefer the main MinerU markdown file for the current PDF.
    Fall back to other markdown, txt, then json outputs.
    """

    preferred_md = output_root / f"{pdf_stem}.md"
    if preferred_md.exists():
        return preferred_md

    candidate_files: list[Path] = []
    candidate_files.extend(output_root.rglob("*.md"))
    candidate_files.extend(output_root.rglob("*.txt"))
    candidate_files.extend(output_root.rglob("*.json"))

    if not candidate_files:
        raise ParserError(
            f"MinerU completed, but no .md/.txt/.json output was found in {output_root}"
        )

    suffix_priority = {
        ".md": 0,
        ".txt": 1,
        ".json": 2,
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
    Extract structured text from a PDF using the MinerU CLI.

    This version uses the working MinerU configuration:

        -m txt -b pipeline

    MinerU writes its raw artifacts under:

        outputs/<pdf_stem>/parser_outputs/mineru_run_txt/

    The benchmark runner separately saves normalized text as:

        outputs/<pdf_stem>/parser_outputs/mineru.txt
    """

    pdf = require_pdf(pdf_path)

    mineru_exe = shutil.which("mineru")
    if mineru_exe is None:
        raise ParserError(
            "MinerU CLI was not found in PATH. Install it first with "
            "`pip install -U mineru` or `uv pip install -U \"mineru[core]\"`."
        )

    parser_output_dir = Path(
        os.environ.get(
            "SCRIPTORIUM_PARSER_OUTPUT_DIR",
            str(Path("outputs") / pdf.stem / "parser_outputs"),
        )
    )

    output_root = parser_output_dir / "mineru_run_txt"

    if output_root.exists():
        shutil.rmtree(output_root)

    output_root.mkdir(parents=True, exist_ok=True)

    cmd = [
        mineru_exe,
        "-p",
        str(pdf),
        "-o",
        str(output_root),
        "-m",
        "txt",
        "-b",
        "pipeline",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise ParserError(
            "MinerU failed.\n"
            f"Command:\n{' '.join(cmd)}\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )

    output_root = _flatten_mineru_output(output_root, pdf.stem)

    best_output = _select_best_text_output(output_root, pdf.stem)
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
            "method": "txt",
            "backend": "pipeline",
            "flattened_output": True,
        },
        artifacts=artifacts,
        raw={
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        },
    )