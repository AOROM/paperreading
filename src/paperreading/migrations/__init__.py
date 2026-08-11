"""Versioned migrations for public PaperReading artifacts."""

from paperreading.migrations.v02_to_v03 import migrate_v02_to_v03

__all__ = ["migrate_v02_to_v03"]
