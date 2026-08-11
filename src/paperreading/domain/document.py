"""Source-aware document models used before research extraction."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import ConfigDict, Field, model_validator

from paperreading.domain.base import DomainModel


class DocumentFormat(str, Enum):
    TEXT = "text"
    MARKDOWN = "markdown"
    PDF = "pdf"
    LEGACY_RECORD = "legacy_record"


class BlockKind(str, Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    OTHER = "other"


class DocumentManifest(DomainModel):
    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    format: DocumentFormat
    media_type: str = Field(min_length=1)
    sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    size_bytes: int = Field(default=0, ge=0)
    page_count: int = Field(default=0, ge=0)
    stored_path: str | None = None
    ingested_at: datetime

    @model_validator(mode="after")
    def require_timezone(self) -> DocumentManifest:
        if self.ingested_at.tzinfo is None or self.ingested_at.utcoffset() is None:
            raise ValueError("ingested_at must include a timezone")
        return self


class DocumentBlock(DomainModel):
    block_id: str = Field(min_length=1)
    page: int = Field(ge=1)
    kind: BlockKind
    text: str = Field(min_length=1)
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=1)
    section_path: list[str] = Field(default_factory=list)
    text_hash: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_offsets(self) -> DocumentBlock:
        if self.char_end <= self.char_start:
            raise ValueError("block char_end must be greater than char_start")
        normalized = re.sub(r"\s+", " ", self.text).strip()
        expected = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        if self.text_hash != expected:
            raise ValueError("block text_hash does not match block text")
        return self


class DocumentPage(DomainModel):
    # Source text is an evidence surface; global string stripping would invalidate
    # character offsets and hashes.
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=False,
        validate_assignment=True,
    )

    page_number: int = Field(ge=1)
    text: str
    blocks: list[DocumentBlock] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_blocks(self) -> DocumentPage:
        for block in self.blocks:
            if block.page != self.page_number:
                raise ValueError("block page must match its containing page")
            if block.char_end > len(self.text):
                raise ValueError("block character range exceeds page text")
            excerpt = self.text[block.char_start : block.char_end].strip()
            if excerpt != block.text:
                raise ValueError("block text must match its page character range")
        block_ids = [block.block_id for block in self.blocks]
        if len(block_ids) != len(set(block_ids)):
            raise ValueError("block IDs must be unique within a page")
        return self


class PaperDocument(DomainModel):
    schema_version: Literal["0.3"] = "0.3"
    document_id: str = Field(min_length=1)
    manifest: DocumentManifest
    pages: list[DocumentPage] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_document_structure(self) -> PaperDocument:
        if self.document_id != self.manifest.source_id:
            raise ValueError("document_id must equal manifest.source_id")
        if self.manifest.page_count != len(self.pages):
            raise ValueError("manifest.page_count must equal the number of pages")
        page_numbers = [page.page_number for page in self.pages]
        if len(page_numbers) != len(set(page_numbers)):
            raise ValueError("page numbers must be unique")
        if page_numbers != sorted(page_numbers):
            raise ValueError("pages must be ordered by page_number")
        block_ids = [block.block_id for page in self.pages for block in page.blocks]
        if len(block_ids) != len(set(block_ids)):
            raise ValueError("block IDs must be unique")
        return self

    def block_index(self) -> dict[str, DocumentBlock]:
        return {block.block_id: block for page in self.pages for block in page.blocks}
