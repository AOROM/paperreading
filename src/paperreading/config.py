"""Typed project configuration loaded from .paperreading/config.toml."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import Field

from paperreading.domain.base import DomainModel
from paperreading.utils import atomic_write_text

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10 CI
    import tomli as tomllib


DEFAULT_CONFIG = """config_version = "0.3"

[general]
language = "zh-CN"

[output]
default_format = "markdown"

[evidence]
require_locator = true
minimum_quote_match = 0.95

[excel]
sheet_zh = "中文"
sheet_en = "英文"

[storage]
directory = ".paperreading"
"""


class GeneralConfig(DomainModel):
    language: str = "zh-CN"


class OutputConfig(DomainModel):
    default_format: Literal["json", "markdown", "excel"] = "markdown"


class EvidenceConfig(DomainModel):
    require_locator: bool = True
    minimum_quote_match: float = Field(default=0.95, ge=0, le=1)


class ExcelConfig(DomainModel):
    sheet_zh: str = Field(default="中文", min_length=1)
    sheet_en: str = Field(default="英文", min_length=1)


class StorageConfig(DomainModel):
    directory: str = Field(default=".paperreading", min_length=1)


class PaperReadingConfig(DomainModel):
    config_version: Literal["0.3"] = "0.3"
    general: GeneralConfig = Field(default_factory=GeneralConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    evidence: EvidenceConfig = Field(default_factory=EvidenceConfig)
    excel: ExcelConfig = Field(default_factory=ExcelConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)

    def stable_hash(self) -> str:
        payload = json.dumps(
            self.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def config_path(project: Path) -> Path:
    return project.expanduser().resolve() / ".paperreading" / "config.toml"


def load_config(project: Path) -> PaperReadingConfig:
    path = config_path(project)
    if not path.exists():
        return PaperReadingConfig()
    with path.open("rb") as stream:
        payload = tomllib.load(stream)
    return PaperReadingConfig.model_validate(payload)


def write_default_config(project: Path, *, force: bool = False) -> Path:
    path = config_path(project)
    atomic_write_text(path, DEFAULT_CONFIG, force=force)
    return path
