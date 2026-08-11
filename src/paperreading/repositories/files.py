"""Atomic, inspectable JSON repository under .paperreading/."""

from __future__ import annotations

import json
import re
from pathlib import Path

from paperreading.config import config_path, load_config, write_default_config
from paperreading.domain import PaperDocument, PaperDraft, PaperPackage
from paperreading.utils import atomic_write_json

SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _safe_id(value: str) -> str:
    if not SAFE_ID_RE.fullmatch(value):
        raise ValueError(f"unsafe artifact identifier: {value!r}")
    return value


class FileRepository:
    def __init__(self, project: Path) -> None:
        self.project = project.expanduser().resolve()
        config = load_config(self.project)
        configured = Path(config.storage.directory)
        self.root = (
            configured if configured.is_absolute() else self.project / configured
        ).resolve()

    def initialize(self, *, force_config: bool = False) -> Path:
        if force_config:
            write_default_config(self.project, force=True)
            self.root = (self.project / ".paperreading").resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        for name in ("documents", "drafts", "records", "analyses", "audits", "cache"):
            (self.root / name).mkdir(exist_ok=True)
        config = config_path(self.project)
        if not config.exists():
            write_default_config(self.project)
        manifest = self.root / "manifest.json"
        if not manifest.exists():
            atomic_write_json(
                manifest,
                {"schema_version": "0.3", "documents": {}, "records": {}},
                force=False,
            )
        return self.root

    def _update_manifest(self, category: str, identifier: str, path: Path) -> None:
        manifest_path = self.root / "manifest.json"
        if manifest_path.exists():
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        else:
            payload = {"schema_version": "0.3", "documents": {}, "records": {}}
        payload.setdefault(category, {})[identifier] = str(path.relative_to(self.root))
        atomic_write_json(manifest_path, payload, force=True)

    def save_document(self, document: PaperDocument, *, force: bool = False) -> Path:
        self.initialize()
        identifier = _safe_id(document.document_id)
        path = self.root / "documents" / f"{identifier}.json"
        atomic_write_json(
            path, document.model_dump(mode="json", exclude_none=True), force=force
        )
        self._update_manifest("documents", identifier, path)
        return path

    def load_document(self, document_id: str) -> PaperDocument:
        identifier = _safe_id(document_id)
        path = self.root / "documents" / f"{identifier}.json"
        return PaperDocument.model_validate_json(path.read_text(encoding="utf-8"))

    def save_draft(self, draft: PaperDraft, *, force: bool = False) -> Path:
        self.initialize()
        identifier = _safe_id(draft.draft_id)
        path = self.root / "drafts" / f"{identifier}.json"
        atomic_write_json(
            path, draft.model_dump(mode="json", exclude_none=True), force=force
        )
        return path

    def save_package(self, package: PaperPackage, *, force: bool = False) -> Path:
        self.initialize()
        identifier = _safe_id(package.record.paper_id)
        path = self.root / "records" / f"{identifier}.json"
        atomic_write_json(
            path, package.model_dump(mode="json", exclude_none=True), force=force
        )
        self._update_manifest("records", identifier, path)
        return path

    def load_package(self, paper_id: str) -> PaperPackage:
        identifier = _safe_id(paper_id)
        path = self.root / "records" / f"{identifier}.json"
        return PaperPackage.model_validate_json(path.read_text(encoding="utf-8"))
