"""Machine-readable validation results."""

from enum import Enum

from pydantic import Field

from paperreading.domain.base import DomainModel


class IssueSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


class ValidationIssue(DomainModel):
    code: str = Field(min_length=1)
    severity: IssueSeverity
    message: str = Field(min_length=1)
    path: str | None = None


class ValidationReport(DomainModel):
    valid: bool
    issues: list[ValidationIssue]
    evidence_count: int = Field(ge=0)
    finding_count: int = Field(ge=0)
