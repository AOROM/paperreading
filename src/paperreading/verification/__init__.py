"""Deterministic source-content verification."""

from paperreading.verification.evidence import (
    PackageVerificationReport,
    apply_verification,
    best_quote_match,
    verify_package,
    verify_span,
)

__all__ = [
    "PackageVerificationReport",
    "apply_verification",
    "best_quote_match",
    "verify_package",
    "verify_span",
]
