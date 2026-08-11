"""Reviewable Markdown export with inline evidence provenance."""

from __future__ import annotations

from pathlib import Path

from paperreading.artifacts import ResearchArtifact
from paperreading.domain import EvidenceRef, EvidenceSpan, PaperPackage, PaperRecord
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


def _span_label(item: EvidenceSpan) -> str:
    locators = [f"id={item.evidence_id}", f"source={item.source_id}"]
    if item.page:
        locators.append(f"page={item.page}")
    if item.section_path:
        locators.append(f"section={' > '.join(item.section_path)}")
    if item.block_id:
        locators.append(f"block={item.block_id}")
    for name in ("table", "column", "figure", "equation", "appendix"):
        value = getattr(item, name)
        if value:
            locators.append(f"{name}={value}")
    status = item.verification.status.value if item.verification else "not_run"
    locators.append(f"verification={status}")
    return ", ".join(locators)


def _v02_record_markdown(record: PaperRecord) -> str:
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


def _package_markdown(package: PaperPackage) -> str:
    record = package.record
    metadata = record.metadata
    lines = [
        f"# {metadata.title}",
        "",
        f"- Paper ID: `{record.paper_id}`",
        f"- Schema: `{package.schema_version}`",
        f"- Package state: `{package.state.value}`",
        f"- Record type: `{record.record_type.value}`",
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
    lines.extend(["", "## Source-grounded claims", ""])
    for claim in record.source_claims:
        lines.append(f"- {claim.statement}")
        lines.extend(f"  - Evidence: `{item}`" for item in claim.evidence_ids)

    lines.extend(["", "## Reported findings", ""])
    if record.findings:
        for finding in record.findings:
            lines.append(
                f"- {finding.statement} ({finding.relationship.value}; "
                f"{finding.language_strength.value})"
            )
            lines.extend(f"  - Evidence: `{item}`" for item in finding.evidence_ids)
    else:
        lines.append("- No empirical finding recorded.")

    lines.extend(["", "## Paper-reported limitations", ""])
    if record.limitations:
        lines.extend(
            f"- {item.statement} (origin: `{item.origin.value}`)"
            for item in record.limitations
        )
    else:
        lines.append("- No paper-reported limitation recorded.")

    lines.extend(["", "## Research analysis", ""])
    if package.analysis and package.analysis.assessments:
        lines.append("### Assessments")
        lines.append("")
        lines.extend(
            f"- {item.statement} (origin: `{item.origin.value}`)"
            for item in package.analysis.assessments
        )
        lines.append("")
    else:
        lines.append("- No separate assessment recorded.")
        lines.append("")

    if package.analysis and package.analysis.research_extensions:
        lines.append("### Research extensions")
        lines.append("")
        for extension in package.analysis.research_extensions:
            lines.append(f"#### {extension.title}")
            lines.append("")
            lines.append(extension.research_question)
            if extension.identification_strategy:
                lines.append(f"- Identification: {extension.identification_strategy}")
            if extension.data_sources:
                lines.append(f"- Data: {', '.join(extension.data_sources)}")
            if extension.falsification:
                lines.append(f"- Falsification: {extension.falsification}")
            if extension.assumptions:
                lines.extend(f"- Assumption: {item}" for item in extension.assumptions)
            lines.append("")

    lines.extend(["## Evidence index", ""])
    for evidence_id in sorted(package.evidence_index):
        evidence = package.evidence_index[evidence_id]
        lines.append(f"- {_span_label(evidence)}")
        if evidence.quoted_text:
            lines.append(f"  - Quote: {evidence.quoted_text}")

    if package.migration_notes:
        lines.extend(["", "## Migration notes", ""])
        lines.extend(f"- {item}" for item in package.migration_notes)
    return "\n".join(lines).rstrip() + "\n"


def _artifact_markdown(artifact: ResearchArtifact) -> str:
    if isinstance(artifact, PaperPackage):
        return _package_markdown(artifact)
    return _v02_record_markdown(artifact)


class MarkdownExporter:
    def export(
        self,
        records: list[ResearchArtifact],
        destination: Path,
        **options: object,
    ) -> ExportResult:
        force = bool(options.get("force", False))
        content = "\n---\n\n".join(_artifact_markdown(record) for record in records)
        atomic_write_text(destination, content, force=force)
        return ExportResult(
            action="records_exported",
            format="markdown",
            destination=str(destination.expanduser().resolve()),
            records=len(records),
        )
