"""Command-line interface for the PaperReading Core."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Annotated, NoReturn

import typer
from pydantic import ValidationError

from paperreading import __version__
from paperreading.application import (
    ExtractDocument,
    ExtractionBundle,
    FinalizeDraft,
    IngestDocument,
    MigrateRecord,
    ReviewDecisions,
    ReviewDraft,
    VerifyPackage,
)
from paperreading.artifacts import ResearchArtifact, load_artifact
from paperreading.config import load_config
from paperreading.domain import (
    EvidenceRef,
    EvidenceSpan,
    PaperDocument,
    PaperDraft,
    PaperPackage,
    PaperRecord,
)
from paperreading.domain.base import DomainModel
from paperreading.exporters import ExportFormat, JsonExporter, MarkdownExporter
from paperreading.exporters.text import atomic_write_text
from paperreading.projections import to_legacy_13_fields
from paperreading.providers import JsonExtractionManifest, JsonExtractionProvider
from paperreading.repositories import FileRepository
from paperreading.validation import validate_package, validate_record
from paperreading.validation.result import ValidationReport

app = typer.Typer(
    name="paperreading",
    help="Evidence-grounded AI research workflow for versioned paper artifacts.",
    no_args_is_help=True,
    add_completion=False,
)


def _abort(message: str, *, code: int = 1) -> NoReturn:
    typer.echo(
        json.dumps({"action": "error", "message": message}, ensure_ascii=False),
        err=True,
    )
    raise typer.Exit(code)


def _print_json(payload: object) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


def _optional_datetime(value: str | None, *, option: str) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(
            f"{option} must be an ISO 8601 timestamp with a timezone"
        ) from exc


def _model_json(model: DomainModel) -> str:
    return (
        json.dumps(
            model.model_dump(mode="json", exclude_none=True),
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )


def _artifact_report(
    artifact: ResearchArtifact, *, strict: bool = False
) -> ValidationReport:
    if isinstance(artifact, PaperPackage):
        return validate_package(artifact, strict=strict)
    return validate_record(artifact, strict=strict)


@app.command()
def version() -> None:
    """Print the installed PaperReading version."""

    typer.echo(__version__)


@app.command("init")
def initialize(
    directory: Annotated[
        Path, typer.Argument(help="Research project directory.")
    ] = Path("."),
    force: Annotated[
        bool, typer.Option("--force", help="Replace an existing config.")
    ] = False,
) -> None:
    """Create an inspectable local .paperreading project."""

    try:
        repository = FileRepository(directory)
        state_dir = repository.initialize(force_config=force)
    except (OSError, ValidationError, ValueError) as exc:
        _abort(str(exc))
    _print_json(
        {
            "action": "project_initialized",
            "directory": str(state_dir),
            "config": str(
                directory.expanduser().resolve() / ".paperreading/config.toml"
            ),
        }
    )


@app.command()
def validate(
    artifact: Annotated[
        Path, typer.Argument(exists=True, dir_okay=False, readable=True)
    ],
    strict: Annotated[
        bool,
        typer.Option(
            "--strict",
            help="Require structural locators and fully verified v0.3 evidence.",
        ),
    ] = False,
) -> None:
    """Validate schema, evidence state, and causal language."""

    try:
        research_artifact = load_artifact(artifact)
        report = _artifact_report(research_artifact, strict=strict)
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        _abort(str(exc), code=2)
    _print_json(report.model_dump(mode="json"))
    if not report.valid:
        raise typer.Exit(2)


@app.command()
def migrate(
    record: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
    project: Annotated[Path, typer.Option("--project")] = Path("."),
    persist: Annotated[
        bool,
        typer.Option(
            "--persist", help="Save the package in the project's file repository."
        ),
    ] = False,
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    """Migrate a v0.2 record to a normalized v0.3 package."""

    try:
        artifact = load_artifact(record)
        if not isinstance(artifact, PaperRecord):
            raise ValueError("migrate requires a v0.2 PaperRecord")
        repository = FileRepository(project) if persist else None
        package, persisted_to = MigrateRecord(repository).execute(
            artifact,
            persist=persist,
            force=force,
        )
        content = (
            json.dumps(
                package.model_dump(mode="json", exclude_none=True),
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        )
        if output is not None:
            atomic_write_text(output, content, force=force)
        if output is None and not persist:
            typer.echo(content, nl=False)
            return
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        _abort(str(exc), code=2)

    _print_json(
        {
            "action": "record_migrated",
            "schema_version": package.schema_version,
            "output": str(output.expanduser().resolve()) if output else None,
            "repository_path": str(persisted_to) if persisted_to else None,
        }
    )


@app.command()
def ingest(
    source: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    project: Annotated[Path, typer.Option("--project")] = Path("."),
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
    ingested_at: Annotated[
        str | None,
        typer.Option(
            "--ingested-at",
            help="ISO 8601 timestamp with timezone for reproducible ingestion.",
        ),
    ] = None,
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    """Ingest UTF-8 text, Markdown, or a text-based PDF."""

    try:
        repository = FileRepository(project)
        document, destination = IngestDocument(repository).execute(
            source,
            ingested_at=_optional_datetime(ingested_at, option="--ingested-at"),
            force=force,
        )
        if output is not None and output.expanduser().resolve() != destination:
            atomic_write_text(output, _model_json(document), force=force)
    except (OSError, RuntimeError, UnicodeError, ValidationError, ValueError) as exc:
        _abort(str(exc), code=2)
    _print_json(
        {
            "action": "document_ingested",
            "document_id": document.document_id,
            "format": document.manifest.format.value,
            "pages": len(document.pages),
            "blocks": sum(len(page.blocks) for page in document.pages),
            "source_sha256": document.manifest.sha256,
            "canonical_text_sha256": document.canonical_text_sha256,
            "repository_path": str(destination),
            "output": str(output.expanduser().resolve()) if output else None,
        }
    )


@app.command()
def extract(
    document: Annotated[
        Path, typer.Argument(exists=True, dir_okay=False, readable=True)
    ],
    provider_manifest: Annotated[
        Path,
        typer.Option(
            "--provider-manifest",
            exists=True,
            dir_okay=False,
            readable=True,
            help="Auditable staged extraction JSON.",
        ),
    ],
    output: Annotated[Path, typer.Option("--output", "-o")],
    project: Annotated[Path, typer.Option("--project")] = Path("."),
    created_at: Annotated[
        str | None,
        typer.Option("--created-at", help="ISO 8601 timestamp with timezone."),
    ] = None,
    persist: Annotated[
        bool, typer.Option("--persist", help="Also save the draft in the project.")
    ] = False,
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    """Create an evidence-bearing draft through an extraction provider."""

    try:
        paper_document = PaperDocument.model_validate_json(
            document.read_text(encoding="utf-8")
        )
        provider = JsonExtractionProvider.from_path(provider_manifest)
        repository = FileRepository(project) if persist else None
        bundle, destination = ExtractDocument(repository).execute(
            paper_document,
            provider,
            created_at=_optional_datetime(created_at, option="--created-at"),
            persist=persist,
            force=force,
        )
        atomic_write_text(output, _model_json(bundle), force=force)
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        _abort(str(exc), code=2)
    _print_json(
        {
            "action": "draft_extracted",
            "draft_id": bundle.draft.draft_id,
            "status": bundle.draft.status.value,
            "candidates": len(bundle.draft.candidates),
            "conflicts": len(bundle.draft.conflicts),
            "unresolved_fields": bundle.draft.unresolved_fields,
            "output": str(output.expanduser().resolve()),
            "repository_path": str(destination) if destination else None,
        }
    )


@app.command()
def review(
    bundle: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    output: Annotated[Path, typer.Option("--output", "-o")],
    decisions: Annotated[
        Path | None,
        typer.Option(
            "--decisions",
            exists=True,
            dir_okay=False,
            readable=True,
            help="JSON with selections, dismissed_unresolved_fields, and notes.",
        ),
    ] = None,
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    """Resolve extraction ambiguity through explicit human decisions."""

    try:
        extraction_bundle = ExtractionBundle.model_validate_json(
            bundle.read_text(encoding="utf-8")
        )
        review_decisions = (
            ReviewDecisions.model_validate_json(decisions.read_text(encoding="utf-8"))
            if decisions
            else ReviewDecisions()
        )
        reviewed = ReviewDraft().execute(
            extraction_bundle,
            selections=review_decisions.selections,
            dismissed_unresolved_fields=review_decisions.dismissed_unresolved_fields,
            notes=review_decisions.notes,
        )
        atomic_write_text(output, _model_json(reviewed), force=force)
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        _abort(str(exc), code=2)
    _print_json(
        {
            "action": "draft_reviewed",
            "draft_id": reviewed.draft.draft_id,
            "status": reviewed.draft.status.value,
            "conflicts": len(reviewed.draft.conflicts),
            "unresolved_fields": reviewed.draft.unresolved_fields,
            "output": str(output.expanduser().resolve()),
        }
    )


@app.command()
def finalize(
    bundle: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    document: Annotated[
        Path,
        typer.Option("--document", exists=True, dir_okay=False, readable=True),
    ],
    output: Annotated[Path, typer.Option("--output", "-o")],
    project: Annotated[Path, typer.Option("--project")] = Path("."),
    finalized_at: Annotated[
        str | None,
        typer.Option("--finalized-at", help="ISO 8601 timestamp with timezone."),
    ] = None,
    persist: Annotated[
        bool, typer.Option("--persist", help="Also save the package in the project.")
    ] = False,
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    """Turn a reviewed draft into a canonical v0.3 package."""

    try:
        extraction_bundle = ExtractionBundle.model_validate_json(
            bundle.read_text(encoding="utf-8")
        )
        paper_document = PaperDocument.model_validate_json(
            document.read_text(encoding="utf-8")
        )
        repository = FileRepository(project) if persist else None
        package, destination = FinalizeDraft(repository).execute(
            extraction_bundle,
            paper_document,
            finalized_at=_optional_datetime(finalized_at, option="--finalized-at"),
            persist=persist,
            force=force,
        )
        atomic_write_text(output, _model_json(package), force=force)
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        _abort(str(exc), code=2)
    _print_json(
        {
            "action": "draft_finalized",
            "paper_id": package.record.paper_id,
            "state": package.state.value,
            "output": str(output.expanduser().resolve()),
            "repository_path": str(destination) if destination else None,
        }
    )


@app.command()
def read(
    source: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    provider_manifest: Annotated[
        Path,
        typer.Option(
            "--provider-manifest",
            exists=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    output: Annotated[Path, typer.Option("--output", "-o")],
    project: Annotated[Path, typer.Option("--project")] = Path("."),
    ingested_at: Annotated[str | None, typer.Option("--ingested-at")] = None,
    created_at: Annotated[str | None, typer.Option("--created-at")] = None,
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    """Ingest a source and produce a reviewable extraction bundle."""

    try:
        repository = FileRepository(project)
        paper_document, document_path = IngestDocument(repository).execute(
            source,
            ingested_at=_optional_datetime(ingested_at, option="--ingested-at"),
            force=force,
        )
        provider = JsonExtractionProvider.from_path(provider_manifest)
        bundle, draft_path = ExtractDocument(repository).execute(
            paper_document,
            provider,
            created_at=_optional_datetime(created_at, option="--created-at"),
            persist=True,
            force=force,
        )
        atomic_write_text(output, _model_json(bundle), force=force)
    except (
        OSError,
        RuntimeError,
        UnicodeError,
        json.JSONDecodeError,
        ValidationError,
        ValueError,
    ) as exc:
        _abort(str(exc), code=2)
    _print_json(
        {
            "action": "paper_read",
            "document_id": paper_document.document_id,
            "draft_id": bundle.draft.draft_id,
            "status": bundle.draft.status.value,
            "document_path": str(document_path),
            "draft_path": str(draft_path),
            "output": str(output.expanduser().resolve()),
            "next": "review the bundle, then run paperreading finalize",
        }
    )


@app.command()
def verify(
    package: Annotated[
        Path, typer.Argument(exists=True, dir_okay=False, readable=True)
    ],
    document: Annotated[
        Path,
        typer.Option(
            "--document",
            exists=True,
            dir_okay=False,
            readable=True,
            help="PaperDocument JSON.",
        ),
    ],
    project: Annotated[Path, typer.Option("--project")] = Path("."),
    strict: Annotated[bool, typer.Option("--strict")] = False,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    """Check v0.3 evidence locators and quotations against a document."""

    try:
        artifact = load_artifact(package)
        if not isinstance(artifact, PaperPackage):
            raise ValueError("verify requires a v0.3 PaperPackage")
        paper_document = PaperDocument.model_validate_json(
            document.read_text(encoding="utf-8")
        )
        config = load_config(project)
        updated, report, _ = VerifyPackage().execute(
            artifact,
            paper_document,
            strict=strict,
            minimum_quote_match=config.evidence.minimum_quote_match,
        )
        if output is not None:
            content = (
                json.dumps(
                    updated.model_dump(mode="json", exclude_none=True),
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n"
            )
            atomic_write_text(output, content, force=force)
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        _abort(str(exc), code=2)
    payload = report.model_dump(mode="json")
    payload["action"] = "package_verified"
    payload["output"] = str(output.expanduser().resolve()) if output else None
    _print_json(payload)
    if not report.valid:
        raise typer.Exit(2)


@app.command()
def project(
    artifact: Annotated[
        Path, typer.Argument(exists=True, dir_okay=False, readable=True)
    ],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    """Project a v0.2 record or v0.3 package to legacy 13-field JSON."""

    try:
        research_artifact = load_artifact(artifact)
        payload = to_legacy_13_fields(research_artifact)
        content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        if output is not None:
            atomic_write_text(output, content, force=force)
            _print_json(
                {
                    "action": "legacy_projection_written",
                    "destination": str(output.expanduser().resolve()),
                }
            )
        else:
            typer.echo(content, nl=False)
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        _abort(str(exc), code=2)


@app.command("export")
def export_command(
    artifact: Annotated[
        Path, typer.Argument(exists=True, dir_okay=False, readable=True)
    ],
    destination: Annotated[Path, typer.Argument()],
    format: Annotated[ExportFormat, typer.Option("--format", "-f")] = ExportFormat.JSON,
    sheet: Annotated[str, typer.Option("--sheet")] = "中文",
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    """Export one validated artifact to JSON, Markdown, or legacy Excel."""

    try:
        research_artifact = load_artifact(artifact)
        report = _artifact_report(research_artifact)
        if not report.valid:
            _abort(
                "artifact failed evidence or causal-language validation",
                code=2,
            )

        if format is ExportFormat.JSON:
            result = JsonExporter().export(
                [research_artifact], destination, force=force
            )
        elif format is ExportFormat.MARKDOWN:
            result = MarkdownExporter().export(
                [research_artifact], destination, force=force
            )
        else:
            try:
                from paperreading.exporters.excel import ExcelExporter
            except ModuleNotFoundError:
                _abort(
                    "Excel support is not installed; install paperreading[excel].",
                    code=2,
                )
            result = ExcelExporter().export(
                [research_artifact], destination, sheet=sheet
            )
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        _abort(str(exc), code=2)
    _print_json(result)


@app.command()
def schema(
    kind: Annotated[
        str,
        typer.Option(
            "--kind",
            help=(
                "paper, evidence, package, document, draft, evidence-span, "
                "extraction-bundle, extraction-manifest, or review-decisions"
            ),
        ),
    ] = "paper",
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    """Print or save a machine-readable JSON Schema."""

    schema_models: dict[str, type[DomainModel]] = {
        "paper": PaperRecord,
        "evidence": EvidenceRef,
        "package": PaperPackage,
        "document": PaperDocument,
        "draft": PaperDraft,
        "evidence-span": EvidenceSpan,
        "extraction-bundle": ExtractionBundle,
        "extraction-manifest": JsonExtractionManifest,
        "review-decisions": ReviewDecisions,
    }
    model = schema_models.get(kind)
    if model is None:
        _abort(
            "--kind must be paper, evidence, package, document, draft, "
            "evidence-span, extraction-bundle, extraction-manifest, "
            "or review-decisions",
            code=2,
        )
    content = json.dumps(model.model_json_schema(), ensure_ascii=False, indent=2) + "\n"
    try:
        if output is None:
            typer.echo(content, nl=False)
        else:
            atomic_write_text(output, content, force=force)
            _print_json(
                {
                    "action": "schema_written",
                    "kind": kind,
                    "destination": str(output.expanduser().resolve()),
                }
            )
    except OSError as exc:
        _abort(str(exc), code=2)
