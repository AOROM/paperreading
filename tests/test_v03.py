from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from paperreading import __version__  # noqa: E402
from paperreading.cli import app  # noqa: E402
from paperreading.domain import (  # noqa: E402
    EvidenceSpan,
    PackageState,
    PaperDocument,
    PaperPackage,
    PaperRecord,
    VerificationStatus,
)
from paperreading.exporters import JsonExporter, MarkdownExporter  # noqa: E402
from paperreading.ingestion import TextDocumentParser  # noqa: E402
from paperreading.migrations import migrate_v02_to_v03  # noqa: E402
from paperreading.projections import to_legacy_13_fields  # noqa: E402
from paperreading.repositories import FileRepository  # noqa: E402
from paperreading.validation import validate_package  # noqa: E402
from paperreading.verification import apply_verification, verify_package  # noqa: E402

V02_EXAMPLE = ROOT / "examples" / "paper-record.example.json"
V03_EXAMPLE = ROOT / "examples" / "paper-package.example.json"
SOURCE_EXAMPLE = ROOT / "examples" / "source.example.md"
FIXED_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def load_v02() -> PaperRecord:
    return PaperRecord.model_validate_json(V02_EXAMPLE.read_text(encoding="utf-8"))


def load_v03() -> PaperPackage:
    return PaperPackage.model_validate_json(V03_EXAMPLE.read_text(encoding="utf-8"))


def _normalized_hash(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def make_verifiable_package(document: PaperDocument) -> PaperPackage:
    payload = load_v03().model_dump(mode="json", exclude_none=True)
    payload["document"] = document.manifest.model_dump(mode="json", exclude_none=True)
    payload["record"]["metadata"]["source_id"] = document.document_id
    payload["run"]["source_sha256"] = document.manifest.sha256
    quote = (
        "In the synthetic example, tool adoption is associated with higher measured "
        "specialization."
    )
    block = next(
        item
        for page in document.pages
        for item in page.blocks
        if "tool adoption" in item.text
    )
    for evidence in payload["evidence_index"].values():
        for key in (
            "table",
            "column",
            "figure",
            "equation",
            "appendix",
            "traceability",
            "verification",
        ):
            evidence.pop(key, None)
        evidence.update(
            {
                "source_id": document.document_id,
                "type": "TEXT",
                "page": 1,
                "section_path": block.section_path,
                "block_id": block.block_id,
                "char_start": block.char_start,
                "char_end": block.char_end,
                "quoted_text": quote,
                "text_hash": _normalized_hash(quote),
            }
        )
    return PaperPackage.model_validate(payload)


class MigrationAndPackageTests(unittest.TestCase):
    def test_evidence_span_rejects_unresolvable_character_ranges(self) -> None:
        with self.assertRaisesRegex(ValidationError, "require a block_id"):
            EvidenceSpan(
                evidence_id="ev-invalid",
                source_id="src-invalid",
                type="TEXT",
                page=1,
                char_start=0,
                char_end=4,
                quoted_text="text",
            )

    def test_migration_separates_analysis_and_preserves_legacy_projection(self) -> None:
        record = load_v02()
        package = migrate_v02_to_v03(record, migrated_at=FIXED_TIME)

        self.assertEqual(package.schema_version, "0.3")
        self.assertEqual(package.state, PackageState.MIGRATED)
        self.assertEqual(len(package.evidence_index), 4)
        self.assertEqual(len(package.analysis.research_extensions), 2)
        self.assertEqual(package.record.limitations[0].origin, "legacy_unknown")
        self.assertEqual(to_legacy_13_fields(package), to_legacy_13_fields(record))

    def test_migration_is_deterministic_with_a_fixed_timestamp(self) -> None:
        first = migrate_v02_to_v03(load_v02(), migrated_at=FIXED_TIME)
        second = migrate_v02_to_v03(load_v02(), migrated_at=FIXED_TIME)
        self.assertEqual(first.model_dump(mode="json"), second.model_dump(mode="json"))
        self.assertEqual(first.run.run_id, "run-d7cd0ea2d8129b07")

    def test_package_rejects_unresolved_evidence_ids(self) -> None:
        payload = load_v03().model_dump(mode="json")
        payload["record"]["source_claims"][0]["evidence_ids"] = ["ev-missing"]
        with self.assertRaisesRegex(ValidationError, "unresolved evidence IDs"):
            PaperPackage.model_validate(payload)

    def test_package_rejects_unearned_verified_state(self) -> None:
        payload = load_v03().model_dump(mode="json")
        payload["state"] = "verified"
        with self.assertRaisesRegex(ValidationError, "fully verified"):
            PaperPackage.model_validate(payload)

    def test_migrated_package_reports_unverified_evidence_explicitly(self) -> None:
        report = validate_package(load_v03())
        self.assertTrue(report.valid)
        self.assertEqual(
            {item.code for item in report.issues}, {"EVIDENCE_NOT_VERIFIED"}
        )
        self.assertFalse(validate_package(load_v03(), strict=True).valid)


class IngestionRepositoryAndVerificationTests(unittest.TestCase):
    def test_markdown_ingestion_has_stable_ids_sections_and_offsets(self) -> None:
        parser = TextDocumentParser()
        first = parser.parse(SOURCE_EXAMPLE)
        second = parser.parse(SOURCE_EXAMPLE)
        self.assertEqual(first.document_id, second.document_id)
        self.assertEqual(
            [item.block_id for item in first.pages[0].blocks],
            [item.block_id for item in second.pages[0].blocks],
        )
        source_text = first.pages[0].text
        result_block = next(
            item for item in first.pages[0].blocks if "tool adoption" in item.text
        )
        self.assertEqual(
            result_block.section_path,
            ["Synthetic source for ingestion", "Reported result"],
        )
        self.assertEqual(
            source_text[result_block.char_start : result_block.char_end].strip(),
            result_block.text,
        )

    def test_file_repository_is_atomic_and_refuses_implicit_overwrite(self) -> None:
        document = TextDocumentParser().parse(SOURCE_EXAMPLE)
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            repository = FileRepository(project)
            state = repository.initialize()
            destination = repository.save_document(document)
            self.assertEqual(repository.load_document(document.document_id), document)
            self.assertTrue((state / "manifest.json").is_file())
            self.assertTrue((state / "config.toml").is_file())
            with self.assertRaises(FileExistsError):
                repository.save_document(document)
            self.assertTrue(destination.is_file())

    def test_evidence_verification_updates_package_state(self) -> None:
        document = TextDocumentParser().parse(SOURCE_EXAMPLE)
        package = make_verifiable_package(document)
        report = verify_package(package, document, strict=True)
        self.assertTrue(report.valid)
        self.assertEqual(report.verified_count, 4)
        updated = apply_verification(package, report)
        self.assertEqual(updated.state, PackageState.VERIFIED)
        self.assertTrue(
            all(
                item.verification.status is VerificationStatus.VERIFIED
                for item in updated.evidence_index.values()
            )
        )

    def test_evidence_verification_fails_a_wrong_quote(self) -> None:
        document = TextDocumentParser().parse(SOURCE_EXAMPLE)
        package = make_verifiable_package(document)
        evidence = next(iter(package.evidence_index.values()))
        evidence.quoted_text = "A result that does not occur in the source."
        evidence.text_hash = _normalized_hash(evidence.quoted_text)
        report = verify_package(package, document)
        self.assertFalse(report.valid)
        self.assertEqual(report.failed_count, 1)

    def test_partial_verification_does_not_promote_package_state(self) -> None:
        document = TextDocumentParser().parse(SOURCE_EXAMPLE)
        package = make_verifiable_package(document)
        evidence_id = next(iter(package.evidence_index))
        payload = package.evidence_index[evidence_id].model_dump(mode="json")
        payload.update(
            {
                "block_id": None,
                "char_start": None,
                "char_end": None,
                "quoted_text": None,
                "text_hash": None,
                "table": "Synthetic table",
            }
        )
        package.evidence_index[evidence_id] = EvidenceSpan.model_validate(payload)
        report = verify_package(package, document)
        self.assertTrue(report.valid)
        self.assertEqual(report.partial_count, 1)
        updated = apply_verification(package, report)
        self.assertEqual(updated.state, PackageState.MIGRATED)


class V03InterfaceAndContractTests(unittest.TestCase):
    def test_v03_exporters_preserve_the_package_and_analysis_boundary(self) -> None:
        package = load_v03()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            json_path = root / "package.json"
            markdown_path = root / "package.md"
            JsonExporter().export([package], json_path)
            MarkdownExporter().export([package], markdown_path)
            self.assertEqual(
                PaperPackage.model_validate_json(json_path.read_text(encoding="utf-8")),
                package,
            )
            markdown = markdown_path.read_text(encoding="utf-8")
            self.assertIn("Source-grounded claims", markdown)
            self.assertIn("Research analysis", markdown)
            self.assertIn("Evidence index", markdown)
            self.assertIn("verification=not_run", markdown)

    def test_cli_migrate_ingest_and_verify(self) -> None:
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            migrated_path = root / "migrated.json"
            migrated = runner.invoke(
                app,
                ["migrate", str(V02_EXAMPLE), "--output", str(migrated_path)],
            )
            self.assertEqual(migrated.exit_code, 0, migrated.stdout)
            self.assertEqual(load_v03().schema_version, "0.3")
            self.assertEqual(
                PaperPackage.model_validate_json(
                    migrated_path.read_text(encoding="utf-8")
                ).schema_version,
                "0.3",
            )

            document_path = root / "document.json"
            ingested = runner.invoke(
                app,
                [
                    "ingest",
                    str(SOURCE_EXAMPLE),
                    "--project",
                    str(root),
                    "--output",
                    str(document_path),
                ],
            )
            self.assertEqual(ingested.exit_code, 0, ingested.stdout)
            document = PaperDocument.model_validate_json(
                document_path.read_text(encoding="utf-8")
            )

            verifiable_path = root / "verifiable.json"
            verified_path = root / "verified.json"
            verifiable_path.write_text(
                make_verifiable_package(document).model_dump_json(indent=2),
                encoding="utf-8",
            )
            verified = runner.invoke(
                app,
                [
                    "verify",
                    str(verifiable_path),
                    "--document",
                    str(document_path),
                    "--strict",
                    "--output",
                    str(verified_path),
                ],
            )
            self.assertEqual(verified.exit_code, 0, verified.stdout)
            self.assertTrue(json.loads(verified.stdout)["valid"])
            self.assertEqual(
                PaperPackage.model_validate_json(
                    verified_path.read_text(encoding="utf-8")
                ).state,
                PackageState.VERIFIED,
            )

    def test_versioned_schemas_and_examples_are_current(self) -> None:
        self.assertEqual(__version__, "0.3.0")
        commands = (
            [sys.executable, "tools/export_schemas.py", "--check"],
            [sys.executable, "tools/generate_examples.py", "--check"],
        )
        for command in commands:
            result = subprocess.run(
                command,
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
        expected = (
            "schemas/v0.2/paper.schema.json",
            "schemas/v0.2/evidence.schema.json",
            "schemas/v0.3/package.schema.json",
            "schemas/v0.3/document.schema.json",
            "schemas/v0.3/draft.schema.json",
            "schemas/v0.3/evidence-span.schema.json",
        )
        self.assertTrue(all((ROOT / path).is_file() for path in expected))


if __name__ == "__main__":
    unittest.main()
