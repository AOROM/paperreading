"""Load and normalize public PaperReading research artifacts."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import TypeAlias

from paperreading.domain.package import PaperPackage
from paperreading.domain.paper import PaperRecord
from paperreading.migrations import migrate_v02_to_v03

ResearchArtifact: TypeAlias = PaperRecord | PaperPackage


def parse_artifact(payload: object) -> ResearchArtifact:
    if not isinstance(payload, dict):
        raise ValueError("research artifact must be a JSON object")
    version = payload.get("schema_version")
    if version == "0.2":
        return PaperRecord.model_validate(payload)
    if version == "0.3" and "record" in payload:
        return PaperPackage.model_validate(payload)
    raise ValueError(f"unsupported research artifact schema: {version!r}")


def load_artifact(path: Path) -> ResearchArtifact:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return parse_artifact(payload)


def as_package(
    artifact: ResearchArtifact,
    *,
    migrated_at: datetime | None = None,
) -> PaperPackage:
    if isinstance(artifact, PaperPackage):
        return artifact
    return migrate_v02_to_v03(artifact, migrated_at=migrated_at)
