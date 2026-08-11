"""Small dependency-free utilities shared across adapters."""

from paperreading.utils.files import atomic_write_json, atomic_write_text

__all__ = ["atomic_write_json", "atomic_write_text"]
