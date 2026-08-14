from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from paperreading.application import (  # noqa: E402
    ExtractDocument,
    ExtractionBundle,
    FinalizeDraft,
    ReviewDraft,
)
from paperreading.cli import app  # noqa: E402
from paperreading.domain import (  # noqa: E402
    DraftStatus,
    ExtractionCandidate,
    PackageState,
    PaperPackage,
)
from paperreading.ingestion import PdfDocumentParser, TextDocumentParser  # noqa: E402
from paperreading.providers import (  # noqa: E402
    ExtractionStage,
    JsonExtractionManifest,
    JsonExtractionProvider,
)
from paperreading.verification import best_quote_match, verify_package  # noqa: E402

SOURCE = ROOT / "examples" / "source.example.md"
MANIFEST = ROOT / "examples" / "extraction-manifest.example.json"
FIXED_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


class ParserHardeningTests(unittest.TestCase):
    def test_raw_and_canonical_hashes_have_distinct_meanings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lf = root / "lf.md"
            crlf = root / "crlf.md"
            lf.write_bytes(b"# Title\n\nStable text.\n")
            crlf.write_bytes(b"# Title\r\n\r\nStable text.\r\n")
            parser = TextDocumentParser()
            first = parser.parse(lf, ingested_at=FIXED_TIME)
            second = parser.parse(crlf, ingested_at=FIXED_TIME)

        self.assertNotEqual(first.manifest.sha256, second.manifest.sha256)
        self.assertEqual(first.canonical_text_sha256, second.canonical_text_sha256)
        self.assertEqual(first.manifest.ingested_at, FIXED_TIME)

    def test_pdf_adapter_preserves_pages_and_declares_text_only_scope(self) -> None:
        class FakePage:
            def __init__(self, text: str) -> None:
                self.text = text

            def extract_text(self, **kwargs: object) -> str:
                self.kwargs = kwargs
                return self.text

        class FakeReader:
            is_encrypted = False
            pages = [FakePage("First page text."), FakePage("Second page text.")]

        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "paper.pdf"
            source.write_bytes(b"%PDF-1.7 synthetic")
            with patch(
                "paperreading.ingestion.pdf.PdfReader", return_value=FakeReader()
            ):
                document = PdfDocumentParser().parse(
                    source,
                    ingested_at=FIXED_TIME,
                )

        self.assertEqual(document.manifest.page_count, 2)
        self.assertEqual(document.pages[1].blocks[0].block_id, "p2-b0001")
        self.assertEqual(document.manifest.format.value, "pdf")

    def test_pdf_adapter_fails_clearly_without_optional_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "paper.pdf"
            source.write_bytes(b"%PDF-1.7 synthetic")
            with patch("paperreading.ingestion.pdf.PdfReader", None):
                with self.assertRaisesRegex(RuntimeError, r"paperreading\[pdf\]"):
                    PdfDocumentParser().parse(source, ingested_at=FIXED_TIME)


class EvidenceVerificationV2Tests(unittest.TestCase):
    def test_fuzzy_alignment_finds_quote_inside_a_long_context(self) -> None:
        quote = (
            "The treatment estimate remains stable after replacing the outcome "
            "measure and clustering standard errors."
        )
        ocr_context = (
            "Unrelated introduction. " * 80
            + quote.replace("clustering", "c1ustering")
            + " Unrelated appendix material." * 80
        )
        self.assertGreaterEqual(best_quote_match(quote, ocr_context), 0.98)


class ExtractionLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = TextDocumentParser().parse(SOURCE, ingested_at=FIXED_TIME)
        self.manifest = JsonExtractionManifest.model_validate_json(
            MANIFEST.read_text(encoding="utf-8")
        )

    def test_extract_review_finalize_and_verify(self) -> None:
        provider = JsonExtractionProvider(self.manifest)
        bundle, _ = ExtractDocument().execute(
            self.document,
            provider,
            created_at=FIXED_TIME,
        )
        self.assertEqual(bundle.draft.status, DraftStatus.EXTRACTED)
        self.assertEqual(len(bundle.evidence_index), 4)

        reviewed = ReviewDraft().execute(bundle, notes=["Fixture reviewed."])
        self.assertEqual(reviewed.draft.status, DraftStatus.READY_TO_FINALIZE)
        package, _ = FinalizeDraft().execute(
            reviewed,
            self.document,
            finalized_at=FIXED_TIME,
        )
        self.assertEqual(package.state, PackageState.FINALIZED)
        self.assertEqual(package.record.paper_id, "synthetic-demo")
        self.assertEqual(package.run.pipeline_version, "0.3.1")
        self.assertEqual(package.run.provider, "offline-json")
        self.assertEqual(package.run.provider_version, "1.0.0")
        self.assertEqual(
            package.run.canonical_text_sha256,
            self.document.canonical_text_sha256,
        )
        self.assertTrue(verify_package(package, self.document, strict=True).valid)

    def test_draft_identity_is_deterministic_and_covers_evidence(self) -> None:
        provider = JsonExtractionProvider(self.manifest)
        first, _ = ExtractDocument().execute(
            self.document,
            provider,
            created_at=FIXED_TIME,
        )
        second, _ = ExtractDocument().execute(
            self.document,
            provider,
            created_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
        )
        self.assertEqual(first.draft.draft_id, second.draft.draft_id)

        payload = self.manifest.model_dump(mode="python")
        finding = payload["stages"][ExtractionStage.FINDINGS]["evidence_index"][
            "ev-finding"
        ]
        finding["quoted_text"] = "A changed quotation."
        finding["text_hash"] = (
            "6b710f7e00126dbaad6c24505ac07855b7b665744cd4ee065d528e3c801cbd99"
        )
        changed_provider = JsonExtractionProvider(
            JsonExtractionManifest.model_validate(payload)
        )
        changed, _ = ExtractDocument().execute(
            self.document,
            changed_provider,
            created_at=FIXED_TIME,
        )
        self.assertNotEqual(first.draft.draft_id, changed.draft.draft_id)

    def test_finalization_rejects_unreviewed_or_changed_bundle(self) -> None:
        bundle, _ = ExtractDocument().execute(
            self.document,
            JsonExtractionProvider(self.manifest),
            created_at=FIXED_TIME,
        )
        with self.assertRaisesRegex(ValueError, "ready before finalization"):
            FinalizeDraft().execute(bundle, self.document, finalized_at=FIXED_TIME)

        reviewed = ReviewDraft().execute(bundle)
        payload = reviewed.model_dump(mode="python")
        payload["canonical_text_sha256"] = "0" * 64
        changed = ExtractionBundle.model_validate(payload)
        with self.assertRaisesRegex(ValueError, "document text changed"):
            FinalizeDraft().execute(changed, self.document, finalized_at=FIXED_TIME)

    def test_conflicts_require_an_explicit_human_selection(self) -> None:
        payload = self.manifest.model_dump(mode="python")
        metadata = payload["stages"][ExtractionStage.METADATA]
        metadata["candidates"].append(
            ExtractionCandidate(
                candidate_id="cand-metadata-alternative",
                field_path="record.metadata",
                value={
                    "title": "Conflicting title",
                    "authors": ["Unknown"],
                    "source_id": self.document.document_id,
                    "language": "en",
                },
                evidence_ids=["ev-title"],
                extractor="offline-json",
                prompt_version="fixture-1",
            )
        )
        provider = JsonExtractionProvider(
            JsonExtractionManifest.model_validate(payload)
        )
        bundle, _ = ExtractDocument().execute(
            self.document,
            provider,
            created_at=FIXED_TIME,
        )
        self.assertEqual(bundle.draft.status, DraftStatus.NEEDS_REVIEW)
        self.assertEqual(len(bundle.draft.conflicts), 1)
        still_open = ReviewDraft().execute(bundle)
        self.assertEqual(still_open.draft.status, DraftStatus.NEEDS_REVIEW)

        reviewed = ReviewDraft().execute(
            bundle,
            selections={"record.metadata": "cand-metadata"},
        )
        self.assertEqual(reviewed.draft.status, DraftStatus.READY_TO_FINALIZE)
        self.assertNotIn(
            "Conflicting title",
            [str(item.value) for item in reviewed.draft.candidates],
        )

    def test_provider_cannot_preapprove_its_own_evidence(self) -> None:
        payload = self.manifest.model_dump(mode="python")
        evidence = payload["stages"][ExtractionStage.METADATA]["evidence_index"][
            "ev-title"
        ]
        evidence["verification"] = {
            "status": "verified",
            "source_match": True,
        }
        with self.assertRaisesRegex(ValueError, "cannot contain verification"):
            JsonExtractionManifest.model_validate(payload)

    def test_cli_extract_review_finalize_and_verify(self) -> None:
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document_path = root / "document.json"
            bundle_path = root / "bundle.json"
            reviewed_path = root / "reviewed.json"
            package_path = root / "package.json"

            commands = (
                [
                    "ingest",
                    str(SOURCE),
                    "--project",
                    str(root),
                    "--output",
                    str(document_path),
                    "--ingested-at",
                    "2026-01-01T00:00:00Z",
                ],
                [
                    "extract",
                    str(document_path),
                    "--provider-manifest",
                    str(MANIFEST),
                    "--output",
                    str(bundle_path),
                    "--created-at",
                    "2026-01-01T00:00:00Z",
                ],
                [
                    "review",
                    str(bundle_path),
                    "--decisions",
                    str(ROOT / "examples" / "review-decisions.example.json"),
                    "--output",
                    str(reviewed_path),
                ],
                [
                    "finalize",
                    str(reviewed_path),
                    "--document",
                    str(document_path),
                    "--output",
                    str(package_path),
                    "--finalized-at",
                    "2026-01-01T00:00:00Z",
                ],
                [
                    "verify",
                    str(package_path),
                    "--document",
                    str(document_path),
                    "--strict",
                ],
            )
            results = [runner.invoke(app, command) for command in commands]
            package = PaperPackage.model_validate_json(
                package_path.read_text(encoding="utf-8")
            )

        self.assertTrue(
            all(result.exit_code == 0 for result in results),
            "\n".join(result.stdout for result in results),
        )
        self.assertEqual(package.state, PackageState.FINALIZED)
        self.assertTrue(json.loads(results[-1].stdout)["valid"])

    def test_cli_read_persists_document_and_draft(self) -> None:
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = runner.invoke(
                app,
                [
                    "read",
                    str(SOURCE),
                    "--provider-manifest",
                    str(MANIFEST),
                    "--output",
                    str(root / "bundle.json"),
                    "--project",
                    str(root),
                    "--ingested-at",
                    "2026-01-01T00:00:00Z",
                    "--created-at",
                    "2026-01-01T00:00:00Z",
                ],
            )
            self.assertEqual(result.exit_code, 0, result.stdout)
            payload = json.loads(result.stdout)
            document_path = Path(payload["document_path"])
            draft_path = Path(payload["draft_path"])
            self.assertTrue(document_path.is_file())
            self.assertTrue(draft_path.is_file())

        self.assertEqual(payload["status"], "extracted")


if __name__ == "__main__":
    unittest.main()
