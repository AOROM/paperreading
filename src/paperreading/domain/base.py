"""Shared configuration for strict domain models."""

from pydantic import BaseModel, ConfigDict


class DomainModel(BaseModel):
    """Reject unknown fields so extraction drift fails visibly."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )
