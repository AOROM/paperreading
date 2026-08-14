"""Optional text-based PDF ingestion through the document parser port."""

from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

from paperreading.domain import (
    DocumentFormat,
    DocumentManifest,
    DocumentPage,
    PaperDocument,
)
from paperreading.ingestion.text import (
    blocks_from_text,
    normalize_line_endings,
    resolve_ingested_at,
)

try:
    from pypdf import PdfReader as _PdfReader
except ModuleNotFoundError:  # pragma: no cover - exercised without the optional extra
    _PdfReader = None

PdfReader: Any = _PdfReader


class PdfDocumentParser:
    """Extract a stable text surface from PDFs that already contain text.

    This adapter intentionally does not claim OCR, layout geometry, table
    reconstruction, or figure extraction. Scanned PDFs need an OCR adapter.
    """

    def supports(self, source: Path) -> bool:
        return source.suffix.lower() == ".pdf"

    def parse(
        self,
        source: Path,
        *,
        ingested_at: datetime | None = None,
    ) -> PaperDocument:
        if PdfReader is None:
            raise RuntimeError(
                "PDF support is optional; install it with `pip install "
                "paperreading[pdf]`"
            )

        path = source.expanduser().resolve()
        if not self.supports(path):
            raise ValueError(
                f"unsupported PDF document extension: {path.suffix.lower()}"
            )

        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        source_id = f"src-{digest[:16]}"
        try:
            reader = PdfReader(path)
        except Exception as exc:  # adapter boundary normalizes pypdf-specific errors
            raise ValueError("PDF could not be read") from exc
        if getattr(reader, "is_encrypted", False):
            try:
                unlocked = reader.decrypt("")
            except Exception as exc:  # pypdf exposes several reader-specific errors
                raise ValueError("encrypted PDF could not be opened") from exc
            if not unlocked:
                raise ValueError("encrypted PDF requires a password")

        pages: list[DocumentPage] = []
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                extracted = page.extract_text(
                    extraction_mode="layout",
                    layout_mode_space_vertically=False,
                )
            except Exception as exc:
                raise ValueError(
                    f"text extraction failed on PDF page {page_number}"
                ) from exc
            text = normalize_line_endings(extracted or "")
            pages.append(
                DocumentPage(
                    page_number=page_number,
                    text=text,
                    blocks=blocks_from_text(
                        text,
                        markdown=False,
                        page_number=page_number,
                    ),
                )
            )

        if not pages:
            raise ValueError("PDF contains no pages")
        if not any(page.text.strip() for page in pages):
            raise ValueError(
                "PDF contains no extractable text; scanned documents require OCR"
            )

        return PaperDocument(
            document_id=source_id,
            manifest=DocumentManifest(
                source_id=source_id,
                source_name=path.name,
                format=DocumentFormat.PDF,
                media_type="application/pdf",
                sha256=digest,
                size_bytes=len(raw),
                page_count=len(pages),
                stored_path=None,
                ingested_at=resolve_ingested_at(ingested_at),
            ),
            pages=pages,
        )
