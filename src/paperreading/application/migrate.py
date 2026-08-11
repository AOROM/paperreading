"""Migrate a legacy record and optionally persist the resulting package."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from paperreading.domain import PaperPackage, PaperRecord
from paperreading.migrations import migrate_v02_to_v03
from paperreading.repositories.base import ResearchRepository


@dataclass(frozen=True)
class MigrateRecord:
    repository: ResearchRepository | None = None

    def execute(
        self,
        record: PaperRecord,
        *,
        migrated_at: datetime | None = None,
        persist: bool = False,
        force: bool = False,
    ) -> tuple[PaperPackage, Path | None]:
        package = migrate_v02_to_v03(record, migrated_at=migrated_at)
        destination = None
        if persist:
            if self.repository is None:
                raise ValueError("persist=True requires a repository")
            destination = self.repository.save_package(package, force=force)
        return package, destination
