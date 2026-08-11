"""Deterministic source-content verification."""

from paperreading.verification.evidence import (
    PackageVerificationReport,
    apply_verification,
    verify_package,
    verify_span,
)

__all__ = [
    "PackageVerificationReport",
    "apply_verification",
    "verify_package",
    "verify_span",
]
