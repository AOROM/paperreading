"""Deterministic UTF-8 text and Markdown ingestion."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

from paperreading.domain import (
    BlockKind,
    DocumentBlock,
    DocumentFormat,
    DocumentManifest,
    DocumentPage,
    PaperDocument,
)
from paperreading.ingestion.base import DocumentParser

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


def _hash_text(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def normalize_line_endings(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def resolve_ingested_at(value: datetime | None) -> datetime:
    resolved = value or datetime.now(timezone.utc)
    if resolved.tzinfo is None or resolved.utcoffset() is None:
        raise ValueError("ingested_at must include a timezone")
    return resolved


def blocks_from_text(
    text: str,
    *,
    markdown: bool,
    page_number: int = 1,
) -> list[DocumentBlock]:
    result: list[DocumentBlock] = []
    section_levels: list[str] = []
    lines = text.splitlines(keepends=True)
    paragraph_lines: list[str] = []
    paragraph_start = 0
    offset = 0

    def append_block(
        content: str,
        start: int,
        end: int,
        kind: BlockKind,
        section_path: list[str],
    ) -> None:
        stripped = content.strip()
        if not stripped:
            return
        block_id = f"p{page_number}-b{len(result) + 1:04d}"
        result.append(
            DocumentBlock(
                block_id=block_id,
                page=page_number,
                kind=kind,
                text=stripped,
                char_start=start,
                char_end=end,
                section_path=section_path,
                text_hash=_hash_text(stripped),
            )
        )

    def flush_paragraph(end: int) -> None:
        nonlocal paragraph_lines
        if paragraph_lines:
            append_block(
                "".join(paragraph_lines),
                paragraph_start,
                end,
                BlockKind.PARAGRAPH,
                list(section_levels),
            )
            paragraph_lines = []

    for line in lines:
        line_end = offset + len(line)
        heading = HEADING_RE.match(line.strip()) if markdown else None
        if heading:
            flush_paragraph(offset)
            level = len(heading.group(1))
            title = heading.group(2).strip()
            if len(section_levels) < level:
                section_levels.extend([""] * (level - len(section_levels)))
            section_levels[level - 1] = title
            section_levels[level:] = []
            append_block(
                line,
                offset,
                line_end,
                BlockKind.HEADING,
                [item for item in section_levels if item],
            )
        elif not line.strip():
            flush_paragraph(offset)
        else:
            if not paragraph_lines:
                paragraph_start = offset
            paragraph_lines.append(line)
        offset = line_end
    flush_paragraph(len(text))
    return result


class TextDocumentParser:
    def supports(self, source: Path) -> bool:
        return source.suffix.lower() in {".txt", ".md", ".markdown"}

    def parse(
        self,
        source: Path,
        *,
        ingested_at: datetime | None = None,
    ) -> PaperDocument:
        path = source.expanduser().resolve()
        suffix = path.suffix.lower()
        if not self.supports(path):
            raise ValueError(f"unsupported text document extension: {suffix}")
        raw = path.read_bytes()
        text = normalize_line_endings(raw.decode("utf-8-sig"))
        if not text.strip():
            raise ValueError("source document is empty")
        digest = hashlib.sha256(raw).hexdigest()
        source_id = f"src-{digest[:16]}"
        markdown = suffix in {".md", ".markdown"}
        blocks = blocks_from_text(text, markdown=markdown)
        return PaperDocument(
            document_id=source_id,
            manifest=DocumentManifest(
                source_id=source_id,
                source_name=path.name,
                format=DocumentFormat.MARKDOWN if markdown else DocumentFormat.TEXT,
                media_type="text/markdown" if markdown else "text/plain",
                sha256=digest,
                size_bytes=len(raw),
                page_count=1,
                stored_path=None,
                ingested_at=resolve_ingested_at(ingested_at),
            ),
            pages=[DocumentPage(page_number=1, text=text, blocks=blocks)],
        )


def parser_for_path(path: Path) -> DocumentParser:
    from paperreading.ingestion.pdf import PdfDocumentParser

    parsers: tuple[DocumentParser, ...] = (TextDocumentParser(), PdfDocumentParser())
    for parser in parsers:
        if parser.supports(path):
            return parser
    raise ValueError(
        "no parser is available for this source; supported formats are UTF-8 "
        "text, Markdown, and text-based PDF"
    )
