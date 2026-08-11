"""Canonical, agent-neutral data models used by PaperReading."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class EvidenceRef:
    """A structural source anchor for one research claim."""

    page: int | None = None
    section: str | None = None
    table: str | None = None
    figure: str | None = None
    note: str | None = None

    def validate(self) -> None:
        if self.page is not None and self.page < 1:
            raise ValueError("evidence page must be a positive integer")
        if not any((self.page, self.section, self.table, self.figure, self.note)):
            raise ValueError("evidence reference must contain at least one anchor")


@dataclass
class Finding:
    """A reported result and the source anchors that support it."""

    text: str
    category: str = "baseline"
    coefficient: str | None = None
    significance: str | None = None
    evidence: list[EvidenceRef] = field(default_factory=list)

    def validate(self) -> None:
        if not self.text.strip():
            raise ValueError("finding text cannot be empty")
        for ref in self.evidence:
            ref.validate()


@dataclass
class EmpiricalDesign:
    """Compact representation of an empirical identification design."""

    explanatory_variables: list[str] = field(default_factory=list)
    outcome_variables: list[str] = field(default_factory=list)
    controls: list[str] = field(default_factory=list)
    fixed_effects: list[str] = field(default_factory=list)
    model_type: str | None = None
    identification: str | None = None
    endogeneity: list[str] = field(default_factory=list)
    robustness: list[str] = field(default_factory=list)


@dataclass
class PaperRecord:
    """Canonical structured record for one academic paper."""

    title: str
    authors: list[str] = field(default_factory=list)
    journal: str | None = None
    journal_rankings: list[str] = field(default_factory=list)
    publication_date: str | None = None
    doi: str | None = None
    keywords: list[str] = field(default_factory=list)
    research_questions: list[str] = field(default_factory=list)
    research_logic: str | None = None
    empirical_design: EmpiricalDesign = field(default_factory=EmpiricalDesign)
    findings: list[Finding] = field(default_factory=list)
    mechanisms: list[str] = field(default_factory=list)
    data_sources: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.title.strip():
            raise ValueError("paper title cannot be empty")
        if any(not question.strip() for question in self.research_questions):
            raise ValueError("research questions cannot contain empty values")
        for finding in self.findings:
            finding.validate()

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PaperRecord":
        design_data = data.get("empirical_design") or {}
        findings_data = data.get("findings") or []
        findings = []
        for item in findings_data:
            evidence = [EvidenceRef(**ref) for ref in item.get("evidence", [])]
            finding_data = {key: value for key, value in item.items() if key != "evidence"}
            findings.append(Finding(evidence=evidence, **finding_data))

        known = {
            "title",
            "authors",
            "journal",
            "journal_rankings",
            "publication_date",
            "doi",
            "keywords",
            "research_questions",
            "research_logic",
            "mechanisms",
            "data_sources",
            "limitations",
            "extensions",
        }
        kwargs = {key: data[key] for key in known if key in data}
        record = cls(
            **kwargs,
            empirical_design=EmpiricalDesign(**design_data),
            findings=findings,
        )
        record.validate()
        return record
