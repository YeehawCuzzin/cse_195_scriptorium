from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class PaperMetadata:
    title: str | None
    authors: list[str]
    abstract: str | None
    year: int | None
    doi: str | None
    source: str = "heuristic"
    parser_name: str | None = None


_DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)
_YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


def _clean_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r"^#+\s*", "", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def _nonempty_lines(text: str) -> list[str]:
    lines = [_clean_line(line) for line in text.splitlines()]
    return [line for line in lines if line]


def _looks_like_noise(line: str) -> bool:
    lowered = line.lower()
    noise_prefixes = (
        "--- page",
        "page ",
        "journal of",
        "vol.",
        "copyright",
        "doi:",
        "arxiv:",
    )
    return lowered.startswith(noise_prefixes)


def extract_doi(text: str) -> str | None:
    match = _DOI_RE.search(text)
    if not match:
        return None

    doi = match.group(0).rstrip(".,);]")
    return doi


def extract_year(text: str) -> int | None:
    matches = _YEAR_RE.findall(text)
    year_matches = re.findall(r"\b(?:19|20)\d{2}\b", text)

    if not year_matches:
        return None

    years = [int(year) for year in year_matches]
    reasonable = [year for year in years if 1900 <= year <= 2100]

    if not reasonable:
        return None

    return min(reasonable)


def extract_title(text: str) -> str | None:
    lines = _nonempty_lines(text)

    for line in lines[:40]:
        if _looks_like_noise(line):
            continue
        if line.lower() in {"abstract", "introduction", "references"}:
            continue
        if len(line) < 12:
            continue
        if len(line.split()) < 3:
            continue
        return line

    return None


def extract_authors(text: str, title: str | None = None) -> list[str]:
    lines = _nonempty_lines(text)

    if not lines:
        return []

    start_index = 0

    if title:
        for index, line in enumerate(lines[:50]):
            if line == title:
                start_index = index + 1
                break

    for line in lines[start_index:start_index + 8]:
        lowered = line.lower()

        if _looks_like_noise(line):
            continue
        if lowered.startswith("abstract"):
            break
        if "@" in line:
            continue
        if len(line) > 400:
            continue

        comma_count = line.count(",")
        has_many_names = comma_count >= 2
        has_name_like_words = len(line.split()) >= 2 and any(char.isupper() for char in line)

        if has_many_names or has_name_like_words:
            parts = [part.strip() for part in re.split(r",|;|\band\b", line) if part.strip()]
            cleaned = []

            for part in parts:
                part = re.sub(r"\d+", "", part)
                part = re.sub(r"[*†‡§]", "", part)
                part = _clean_line(part)

                if len(part.split()) >= 2 and len(part) <= 80:
                    cleaned.append(part)

            if cleaned:
                return cleaned

    return []


def extract_abstract(text: str) -> str | None:
    normalized = text.replace("\r\n", "\n")

    patterns = [
        r"(?is)\babstract\b\s*[-—:]?\s*(.*?)(?:\n\s*(?:index terms|keywords|introduction|1\s+introduction)\b)",
        r"(?is)\babstract\b\s*[-—:]?\s*(.*?)(?:\n\s*(?:i\.|1\.)\s+introduction\b)",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized)
        if match:
            abstract = _clean_line(match.group(1))
            if len(abstract) > 40:
                return abstract

    return None


def _crossref_lookup_by_doi(doi: str, mailto: str | None = None) -> dict:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    request = urllib.request.Request(url)

    if mailto:
        request.add_header("User-Agent", f"scriptorium-metadata-prototype (mailto:{mailto})")

    with urllib.request.urlopen(request, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))

    return payload.get("message", {})


def _crossref_lookup_by_title(title: str, mailto: str | None = None) -> dict:
    query = urllib.parse.urlencode({"query.title": title, "rows": 1})
    url = "https://api.crossref.org/works?" + query
    request = urllib.request.Request(url)

    if mailto:
        request.add_header("User-Agent", f"scriptorium-metadata-prototype (mailto:{mailto})")

    with urllib.request.urlopen(request, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))

    items = payload.get("message", {}).get("items", [])
    return items[0] if items else {}


def _metadata_from_crossref(item: dict) -> dict:
    title_list = item.get("title") or []
    abstract = item.get("abstract")
    doi = item.get("DOI")

    authors = []
    for author in item.get("author", []) or []:
        given = author.get("given", "")
        family = author.get("family", "")
        name = " ".join(part for part in [given, family] if part).strip()
        if name:
            authors.append(name)

    year = None
    issued = item.get("issued", {}).get("date-parts", [])
    if issued and issued[0]:
        try:
            year = int(issued[0][0])
        except Exception:
            year = None

    return {
        "title": title_list[0] if title_list else None,
        "authors": authors,
        "abstract": abstract,
        "year": year,
        "doi": doi,
    }


def extract_metadata(
    text: str,
    parser_name: str | None = None,
    crossref_fallback: bool = False,
    mailto: str | None = None,
) -> dict:
    title = extract_title(text)
    authors = extract_authors(text, title=title)
    abstract = extract_abstract(text)
    year = extract_year(text)
    doi = extract_doi(text)

    metadata = PaperMetadata(
        title=title,
        authors=authors,
        abstract=abstract,
        year=year,
        doi=doi,
        parser_name=parser_name,
    )

    if crossref_fallback and (not metadata.title or not metadata.authors or not metadata.year or not metadata.doi):
        try:
            if metadata.doi:
                item = _crossref_lookup_by_doi(metadata.doi, mailto=mailto)
            elif metadata.title:
                item = _crossref_lookup_by_title(metadata.title, mailto=mailto)
            else:
                item = {}

            crossref_data = _metadata_from_crossref(item)

            metadata.title = metadata.title or crossref_data.get("title")
            metadata.authors = metadata.authors or crossref_data.get("authors") or []
            metadata.abstract = metadata.abstract or crossref_data.get("abstract")
            metadata.year = metadata.year or crossref_data.get("year")
            metadata.doi = metadata.doi or crossref_data.get("doi")

            if item:
                metadata.source = "heuristic+crossref"

        except Exception:
            metadata.source = "heuristic_crossref_failed"

    return asdict(metadata)


def extract_metadata_from_file(
    path: str | Path,
    parser_name: str | None = None,
    crossref_fallback: bool = False,
    mailto: str | None = None,
) -> dict:
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    return extract_metadata(
        text=text,
        parser_name=parser_name,
        crossref_fallback=crossref_fallback,
        mailto=mailto,
    )
