"""Persistence ports and local file implementation."""

from paperreading.repositories.base import ResearchRepository
from paperreading.repositories.files import FileRepository

__all__ = ["FileRepository", "ResearchRepository"]
