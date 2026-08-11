"""Core domain models with no interface or storage dependencies."""

from paperreading.domain.evidence import (
    Confidence,
    ConfidenceLevel,
    EvidenceRef,
    EvidenceType,
)
from paperreading.domain.paper import (
    DataDescription,
    DesignType,
    EmpiricalDesign,
    Finding,
    GapType,
    Mechanism,
    PaperMetadata,
    PaperRecord,
    RankingEvidence,
    Relationship,
    ResearchExtension,
    SourceClaim,
    TestResult,
    Theory,
    Variable,
    VariableRole,
)

__all__ = [
    "Confidence",
    "ConfidenceLevel",
    "DataDescription",
    "DesignType",
    "EmpiricalDesign",
    "EvidenceRef",
    "EvidenceType",
    "Finding",
    "GapType",
    "Mechanism",
    "PaperMetadata",
    "PaperRecord",
    "RankingEvidence",
    "Relationship",
    "ResearchExtension",
    "SourceClaim",
    "TestResult",
    "Theory",
    "Variable",
    "VariableRole",
]
