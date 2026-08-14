"""Apply explicit human choices to an extraction bundle."""

from __future__ import annotations

from dataclasses import dataclass

from paperreading.application.workflow import ExtractionBundle
from paperreading.domain import (
    DraftStatus,
    ExtractionCandidate,
    ExtractionConflict,
    PaperDraft,
)


@dataclass(frozen=True)
class ReviewDraft:
    def execute(
        self,
        bundle: ExtractionBundle,
        *,
        selections: dict[str, str] | None = None,
        dismissed_unresolved_fields: list[str] | None = None,
        notes: list[str] | None = None,
    ) -> ExtractionBundle:
        choices = selections or {}
        dismissed = set(dismissed_unresolved_fields or [])
        known_unresolved = set(bundle.draft.unresolved_fields)
        unknown_dismissals = sorted(dismissed - known_unresolved)
        if unknown_dismissals:
            raise ValueError(
                "cannot dismiss unknown unresolved fields: "
                + ", ".join(unknown_dismissals)
            )

        grouped: dict[str, list[ExtractionCandidate]] = {}
        for candidate in bundle.draft.candidates:
            grouped.setdefault(candidate.field_path, []).append(candidate)
        unknown_selections = sorted(set(choices) - set(grouped))
        if unknown_selections:
            raise ValueError(
                "selections reference unknown fields: " + ", ".join(unknown_selections)
            )

        selected: list[ExtractionCandidate] = []
        conflicts: list[ExtractionConflict] = []
        for field_path, candidates in grouped.items():
            selected_id = choices.get(field_path)
            if selected_id is not None:
                matching = [
                    candidate
                    for candidate in candidates
                    if candidate.candidate_id == selected_id
                ]
                if not matching:
                    raise ValueError(
                        f"candidate {selected_id!r} does not belong to {field_path!r}"
                    )
                selected.extend(matching)
            elif len(candidates) == 1:
                selected.extend(candidates)
            else:
                selected.extend(candidates)
                conflicts.append(
                    ExtractionConflict(
                        field_path=field_path,
                        candidate_ids=[item.candidate_id for item in candidates],
                        reason="human selection is required between multiple candidates",
                    )
                )

        remaining_unresolved = [
            field for field in bundle.draft.unresolved_fields if field not in dismissed
        ]
        status = (
            DraftStatus.READY_TO_FINALIZE
            if not conflicts and not remaining_unresolved
            else DraftStatus.NEEDS_REVIEW
        )
        reviewed = PaperDraft(
            draft_id=bundle.draft.draft_id,
            source_id=bundle.draft.source_id,
            status=status,
            candidates=selected,
            unresolved_fields=remaining_unresolved,
            conflicts=conflicts,
            issues=list(
                dict.fromkeys(
                    [
                        *bundle.draft.issues,
                        *(notes or []),
                        *(
                            f"review dismissed unresolved field: {field}"
                            for field in sorted(dismissed)
                        ),
                    ]
                )
            ),
            created_at=bundle.draft.created_at,
        )
        payload = bundle.model_dump(mode="json")
        payload["draft"] = reviewed.model_dump(mode="json")
        return ExtractionBundle.model_validate(payload)
