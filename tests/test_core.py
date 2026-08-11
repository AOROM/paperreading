from __future__ import annotations

import ast
import json
import sys
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from paperreading.cli import app  # noqa: E402
from paperreading.domain import (  # noqa: E402
    ConfidenceLevel,
    DesignType,
    EmpiricalDesign,
    EvidenceRef,
    EvidenceType,
    PaperRecord,
)
from paperreading.exporters import JsonExporter, MarkdownExporter  # noqa: E402
from paperreading.projections import (  # noqa: E402
    LEGACY_FIELDS,
    to_legacy_13_fields,
)
from paperreading.validation import validate_record  # noqa: E402

EXAMPLE = ROOT / "examples" / "paper-record.example.json"


def load_example() -> PaperRecord:
    return PaperRecord.model_validate_json(EXAMPLE.read_text(encoding="utf-8"))


class DomainModelTests(unittest.TestCase):
    def test_example_is_a_strict_rich_record(self) -> None:
        record = load_example()
        self.assertEqual(record.schema_version, "0.2")
        self.assertEqual(record.metadata.source_id, "example-paper-v1")
        self.assertEqual(len(record.extensions), 2)
        self.assertEqual(record.findings[0].evidence[0].confidence.level, "high")

    def test_evidence_requires_text_or_locator(self) -> None:
        with self.assertRaises(ValidationError):
            EvidenceRef(
                source_id="paper-1",
                type=EvidenceType.TEXT,
            )

    def test_confidence_is_rule_derived(self) -> None:
        evidence = EvidenceRef(
            source_id="paper-1",
            type=EvidenceType.TEXT,
            text="Abstract-only statement",
            confidence={
                "score": 1,
                "level": "high",
                "reasons": ["model supplied"],
            },
        )
        self.assertEqual(evidence.confidence.level, ConfidenceLevel.MEDIUM)
        self.assertNotEqual(evidence.confidence.score, 1)

    def test_unknown_domain_fields_are_rejected(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["unsupported"] = True
        with self.assertRaises(ValidationError):
            PaperRecord.model_validate(payload)


class EvidenceValidationTests(unittest.TestCase):
    def test_example_passes_evidence_and_causal_validation(self) -> None:
        report = validate_record(load_example())
        self.assertTrue(report.valid)
        self.assertEqual(report.evidence_count, 4)
        self.assertEqual(report.issues, [])

    def test_strict_mode_rejects_text_without_locator(self) -> None:
        record = load_example()
        record.source_claims[0].evidence[0] = EvidenceRef(
            source_id=record.metadata.source_id,
            type=EvidenceType.TEXT,
            text="Unlocated source claim",
        )
        report = validate_record(record, strict=True)
        self.assertFalse(report.valid)
        self.assertIn("EVIDENCE_LOCATOR_MISSING", {item.code for item in report.issues})

    def test_causal_claim_requires_eligible_identification(self) -> None:
        record = load_example()
        record.empirical_design = EmpiricalDesign(
            type=DesignType.OLS,
            method="Cross-sectional OLS",
            identification_strategy=None,
        )
        record.findings[0].causal = True
        report = validate_record(record)
        self.assertFalse(report.valid)
        self.assertIn("CAUSAL_LANGUAGE_WARNING", {item.code for item in report.issues})


class ProjectionAndExporterTests(unittest.TestCase):
    def test_legacy_projection_is_only_an_output_contract(self) -> None:
        payload = to_legacy_13_fields(load_example())
        self.assertEqual(list(payload), LEGACY_FIELDS[1:])
        self.assertEqual(payload["论文名称"], "示例论文：数字化转型与企业专业化分工")
        self.assertIn("【基准结论】", payload["研究结论"])
        self.assertIn("【机制拓展】", payload["可进一步延伸的研究设计"])

    def test_json_and_markdown_exports_are_traceable(self) -> None:
        record = load_example()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            json_path = root / "record.json"
            markdown_path = root / "record.md"
            JsonExporter().export([record], json_path)
            MarkdownExporter().export([record], markdown_path)

            round_trip = PaperRecord.model_validate_json(
                json_path.read_text(encoding="utf-8")
            )
            self.assertEqual(round_trip.paper_id, record.paper_id)
            markdown = markdown_path.read_text(encoding="utf-8")
            self.assertIn("Reported findings", markdown)
            self.assertIn("table=Table 3", markdown)
            self.assertIn("Researcher assessment", markdown)

    def test_text_export_refuses_implicit_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "record.json"
            destination.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                JsonExporter().export([load_example()], destination)
            self.assertEqual(destination.read_text(encoding="utf-8"), "keep")


class CliAndContractTests(unittest.TestCase):
    def test_cli_validates_and_projects_record(self) -> None:
        runner = CliRunner()
        validated = runner.invoke(app, ["validate", str(EXAMPLE)])
        self.assertEqual(validated.exit_code, 0, validated.stdout)
        self.assertTrue(json.loads(validated.stdout)["valid"])

        projected = runner.invoke(app, ["project", str(EXAMPLE)])
        self.assertEqual(projected.exit_code, 0, projected.stdout)
        self.assertEqual(
            json.loads(projected.stdout)["论文名称"],
            "示例论文：数字化转型与企业专业化分工",
        )

    def test_committed_schemas_are_current(self) -> None:
        for name in ("paper.schema.json", "evidence.schema.json"):
            payload = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            self.assertEqual(payload["$defs"]["EvidenceType"]["enum"][0], "TEXT")

    def test_domain_does_not_import_interfaces_or_adapters(self) -> None:
        forbidden = {"openpyxl", "typer"}
        for path in (SRC / "paperreading" / "domain").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
            self.assertFalse(forbidden & imports, f"forbidden import in {path}")


if __name__ == "__main__":
    unittest.main()
