"""Cross-paper comparison utilities."""

from __future__ import annotations

from collections.abc import Iterable

from .evidence import evidence_coverage
from .models import PaperRecord


MATRIX_COLUMNS = [
    "Title",
    "Journal",
    "Research question",
    "Identification",
    "X",
    "Y",
    "Mechanisms",
    "Main finding",
    "Evidence coverage",
]


def _join(values: list[str]) -> str:
    return "; ".join(value for value in values if value)


def build_literature_matrix(records: Iterable[PaperRecord]) -> list[dict[str, str]]:
    """Convert paper records into dependency-free comparison rows."""

    rows: list[dict[str, str]] = []
    for record in records:
        record.validate()
        design = record.empirical_design
        main_finding = record.findings[0].text if record.findings else ""
        first_question = record.research_questions[0] if record.research_questions else ""
        rows.append(
            {
                "Title": record.title,
                "Journal": record.journal or "",
                "Research question": first_question,
                "Identification": design.identification or design.model_type or "",
                "X": _join(design.explanatory_variables),
                "Y": _join(design.outcome_variables),
                "Mechanisms": _join(record.mechanisms),
                "Main finding": main_finding,
                "Evidence coverage": f"{evidence_coverage(record):.0%}",
            }
        )
    return rows


def matrix_to_markdown(rows: list[dict[str, str]]) -> str:
    """Render Literature Matrix rows as a GitHub-compatible Markdown table."""

    if not rows:
        return ""

    def clean(value: str) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")

    header = "| " + " | ".join(MATRIX_COLUMNS) + " |"
    separator = "| " + " | ".join("---" for _ in MATRIX_COLUMNS) + " |"
    body = [
        "| " + " | ".join(clean(row.get(column, "")) for column in MATRIX_COLUMNS) + " |"
        for row in rows
    ]
    return "\n".join([header, separator, *body])
