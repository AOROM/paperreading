import json
import unittest
from pathlib import Path

from paperreading import (
    EmpiricalDesign,
    EvidenceRef,
    Finding,
    PaperRecord,
    build_literature_matrix,
    evidence_coverage,
    evidence_label,
    matrix_to_markdown,
)


class PaperRecordTests(unittest.TestCase):
    def test_round_trip_from_dict(self):
        source = {
            "title": "Example",
            "research_questions": ["Does X affect Y?"],
            "empirical_design": {
                "explanatory_variables": ["X"],
                "outcome_variables": ["Y"],
                "identification": "DID",
            },
            "findings": [
                {
                    "text": "X increases Y.",
                    "category": "baseline",
                    "evidence": [{"page": 10, "table": "Table 2"}],
                }
            ],
        }
        record = PaperRecord.from_dict(source)
        self.assertEqual(record.title, "Example")
        self.assertEqual(record.empirical_design.identification, "DID")
        self.assertEqual(record.findings[0].evidence[0].page, 10)
        self.assertEqual(record.to_dict()["findings"][0]["text"], "X increases Y.")

    def test_invalid_evidence_page_fails(self):
        with self.assertRaises(ValueError):
            EvidenceRef(page=0).validate()

    def test_empty_evidence_anchor_fails(self):
        with self.assertRaises(ValueError):
            EvidenceRef().validate()


class EvidenceTests(unittest.TestCase):
    def test_label_and_coverage(self):
        grounded = Finding(
            text="Result A",
            evidence=[EvidenceRef(page=12, section="4.2", table="Table 3")],
        )
        ungrounded = Finding(text="Result B")
        record = PaperRecord(title="Example", findings=[grounded, ungrounded])
        self.assertEqual(evidence_label(grounded.evidence[0]), "p. 12 · 4.2 · Table 3")
        self.assertEqual(evidence_coverage(record), 0.5)


class LiteratureMatrixTests(unittest.TestCase):
    def test_matrix_contains_method_variables_and_coverage(self):
        record = PaperRecord(
            title="Example",
            journal="Journal",
            research_questions=["Does X affect Y?"],
            empirical_design=EmpiricalDesign(
                explanatory_variables=["X"],
                outcome_variables=["Y"],
                identification="DID",
            ),
            mechanisms=["M"],
            findings=[Finding(text="X increases Y", evidence=[EvidenceRef(page=9)])],
        )
        rows = build_literature_matrix([record])
        self.assertEqual(rows[0]["Identification"], "DID")
        self.assertEqual(rows[0]["X"], "X")
        self.assertEqual(rows[0]["Y"], "Y")
        self.assertEqual(rows[0]["Evidence coverage"], "100%")
        markdown = matrix_to_markdown(rows)
        self.assertIn("| Title | Journal |", markdown)
        self.assertIn("Example", markdown)

    def test_empty_matrix_is_empty_string(self):
        self.assertEqual(matrix_to_markdown([]), "")


class SchemaTests(unittest.TestCase):
    def test_schema_and_example_are_valid_json(self):
        root = Path(__file__).resolve().parents[1]
        schema = json.loads((root / "schemas" / "paper.schema.json").read_text(encoding="utf-8"))
        example = json.loads((root / "examples" / "paper-record.example.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["title"], "PaperReading PaperRecord")
        self.assertEqual(example["title"], "Digital finance and firm innovation")


if __name__ == "__main__":
    unittest.main()
