from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from parsers.core.base import ParserError, ParserResult, require_pdf


PARSER_NAME = "grobid"
CATEGORY = "structured_metadata"

GROBID_URL = "http://localhost:8070/api/processFulltextDocument"


def _clean_text(text: str) -> str:
    return " ".join(text.split()) if text else ""


def _extract_author_name(author_tag) -> str:
    pers_name = author_tag.find("persName")
    if not pers_name:
        return ""

    name_parts = []

    for forename in pers_name.find_all("forename"):
        text = _clean_text(forename.get_text(" ", strip=True))
        if text:
            name_parts.append(text)

    surname = pers_name.find("surname")
    if surname:
        surname_text = _clean_text(surname.get_text(" ", strip=True))
        if surname_text:
            name_parts.append(surname_text)

    return " ".join(name_parts).strip()


def _structured_result_to_text(result: dict) -> str:
    parts = []

    if result.get("title"):
        parts.append(f"# {result['title']}")

    if result.get("authors"):
        parts.append("Authors: " + ", ".join(result["authors"]))

    if result.get("abstract"):
        parts.append("## Abstract\n" + result["abstract"])

    for section in result.get("sections", []):
        heading = section.get("heading", "")
        text = section.get("text", "")

        if heading and text:
            parts.append(f"## {heading}\n{text}")
        elif heading:
            parts.append(f"## {heading}")
        elif text:
            parts.append(text)

    if result.get("references"):
        references = []

        for ref in result["references"]:
            title = ref.get("title", "")
            raw = ref.get("raw", "")

            if title:
                references.append(title)
            elif raw:
                references.append(raw)

        if references:
            parts.append("## References\n" + "\n".join(references))

    return "\n\n".join(parts)


def extract(pdf_path: str) -> ParserResult:
    """
    Extract structured academic-paper metadata and section text using GROBID.

    Requires a running GROBID server at:
        http://localhost:8070

    This parser is useful for structured metadata such as:
    - title
    - authors
    - abstract
    - sections
    - references
    - raw TEI XML
    """

    pdf = require_pdf(pdf_path)

    try:
        with open(pdf, "rb") as f:
            response = requests.post(
                GROBID_URL,
                files={"input": f},
                timeout=120,
            )

        response.raise_for_status()

    except requests.RequestException as exc:
        raise ParserError(
            "Could not connect to GROBID at localhost:8070. "
            "Start the GROBID server before running this parser."
        ) from exc

    xml_text = response.text
    soup = BeautifulSoup(xml_text, "xml")

    result = {
        "title": "",
        "authors": [],
        "abstract": "",
        "sections": [],
        "references": [],
        "raw_xml": xml_text,
    }

    title_tag = soup.find("title", attrs={"type": "main"})
    if title_tag:
        result["title"] = _clean_text(title_tag.get_text(" ", strip=True))
    else:
        fallback_title = soup.find("title")
        if fallback_title:
            result["title"] = _clean_text(
                fallback_title.get_text(" ", strip=True)
            )

    for author_tag in soup.find_all("author"):
        full_name = _extract_author_name(author_tag)

        if full_name and full_name not in result["authors"]:
            result["authors"].append(full_name)

    abstract_tag = soup.find("abstract")
    if abstract_tag:
        abstract_parts = []

        for p in abstract_tag.find_all("p"):
            text = _clean_text(p.get_text(" ", strip=True))

            if text:
                abstract_parts.append(text)

        if abstract_parts:
            result["abstract"] = "\n\n".join(abstract_parts)
        else:
            result["abstract"] = _clean_text(
                abstract_tag.get_text(" ", strip=True)
            )

    body = soup.find("body")
    if body:
        for div in body.find_all("div", recursive=False):
            heading = ""
            paragraphs = []

            head_tag = div.find("head")
            if head_tag:
                heading = _clean_text(head_tag.get_text(" ", strip=True))

            for p in div.find_all("p"):
                text = _clean_text(p.get_text(" ", strip=True))

                if text:
                    paragraphs.append(text)

            if heading or paragraphs:
                result["sections"].append(
                    {
                        "heading": heading,
                        "text": "\n\n".join(paragraphs),
                    }
                )

    back = soup.find("back")
    if back:
        for bibl in back.find_all("biblStruct"):
            ref_title = ""
            ref_title_tag = bibl.find("title")

            if ref_title_tag:
                ref_title = _clean_text(
                    ref_title_tag.get_text(" ", strip=True)
                )

            ref_authors = []

            for author_tag in bibl.find_all("author"):
                full_name = _extract_author_name(author_tag)

                if full_name:
                    ref_authors.append(full_name)

            result["references"].append(
                {
                    "title": ref_title,
                    "authors": ref_authors,
                    "raw": _clean_text(bibl.get_text(" ", strip=True)),
                }
            )

    text = _structured_result_to_text(result)

    return ParserResult(
        parser_name=PARSER_NAME,
        text=text,
        category=CATEGORY,
        output_format="tei+xml+structured_text",
        metadata={
            "source_file": str(pdf),
            "title": result["title"],
            "authors": result["authors"],
            "section_count": len(result["sections"]),
            "reference_count": len(result["references"]),
            "grobid_url": GROBID_URL,
        },
        artifacts=[],
        raw=result,
    )