"""Verify and optionally persist a v0.3 package."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from paperreading.domain import PaperDocument, PaperPackage
from paperreading.repositories.base import ResearchRepository
from paperreading.verification import (
    PackageVerificationReport,
    apply_verification,
    verify_package,
)


@dataclass(frozen=True)
class VerifyPackage:
    repository: ResearchRepository | None = None

    def execute(
        self,
        package: PaperPackage,
        document: PaperDocument,
        *,
        strict: bool = False,
        minimum_quote_match: float = 0.95,
        persist: bool = False,
        force: bool = False,
    ) -> tuple[PaperPackage, PackageVerificationReport, Path | None]:
        report = verify_package(
            package,
            document,
            strict=strict,
            minimum_quote_match=minimum_quote_match,
        )
        updated = apply_verification(package, report)
        destination = None
        if persist:
            if self.repository is None:
                raise ValueError("persist=True requires a repository")
            destination = self.repository.save_package(updated, force=force)
        return updated, report, destination
