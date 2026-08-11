"""Reviewable Markdown export with inline evidence provenance."""

from __future__ import annotations

from pathlib import Path

from paperreading.domain import EvidenceRef, PaperRecord
from paperreading.exporters.base import ExportResult
from paperreading.exporters.text import atomic_write_text


def _evidence_label(item: EvidenceRef) -> str:
    locators = [f"source={item.source_id}"]
    if item.page:
        locators.append(f"page={item.page}")
    for name in ("section", "table", "column", "figure", "equation", "appendix"):
        value = getattr(item, name)
        if value:
            locators.append(f"{name}={value}")
    if item.confidence:
        locators.append(
            f"confidence={item.confidence.level.value}:{item.confidence.score:.3f}"
        )
    return ", ".join(locators)


def _record_markdown(record: PaperRecord) -> str:
    metadata = record.metadata
    lines = [
        f"# {metadata.title}",
        "",
        f"- Paper ID: `{record.paper_id}`",
        f"- Authors: {', '.join(metadata.authors)}",
        f"- Journal: {metadata.journal or 'Not reported'}",
        f"- Publication date: {metadata.publication_date or 'Not reported'}",
        "",
        "## Research questions",
        "",
    ]
    lines.extend(
        f"{index}. {question}"
        for index, question in enumerate(record.research_questions, start=1)
    )
    lines.extend(["", "## Reported findings", ""])
    for finding in record.findings:
        lines.append(f"- {finding.statement} ({finding.relationship.value})")
        lines.extend(
            f"  - Evidence: {_evidence_label(item)}" for item in finding.evidence
        )

    lines.extend(["", "## Researcher assessment", ""])
    if record.researcher_assessment:
        lines.extend(f"- {item}" for item in record.researcher_assessment)
    else:
        lines.append("- No separate assessment recorded.")

    lines.extend(["", "## Limitations", ""])
    if record.limitations:
        lines.extend(f"- {item}" for item in record.limitations)
    else:
        lines.append("- No limitation recorded.")

    lines.extend(["", "## Research extensions", ""])
    for extension in record.extensions:
        lines.append(f"### {extension.title}")
        lines.append("")
        lines.append(extension.research_question)
        if extension.identification_strategy:
            lines.append(f"- Identification: {extension.identification_strategy}")
        if extension.data_sources:
            lines.append(f"- Data: {', '.join(extension.data_sources)}")
        if extension.falsification:
            lines.append(f"- Falsification: {extension.falsification}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


class MarkdownExporter:
    def export(
        self,
        records: list[PaperRecord],
        destination: Path,
        **options: object,
    ) -> ExportResult:
        force = bool(options.get("force", False))
        content = "\n---\n\n".join(_record_markdown(record) for record in records)
        atomic_write_text(destination, content, force=force)
        return ExportResult(
            action="records_exported",
            format="markdown",
            destination=str(destination.expanduser().resolve()),
            records=len(records),
        )
