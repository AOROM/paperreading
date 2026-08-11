"""Command-line interface for the PaperReading Core."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, NoReturn

import typer
from pydantic import ValidationError

from paperreading import __version__
from paperreading.application import IngestDocument, MigrateRecord, VerifyPackage
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
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    """Ingest a UTF-8 text or Markdown source into a PaperDocument."""

    try:
        repository = FileRepository(project)
        document, destination = IngestDocument(repository).execute(source, force=force)
        if output is not None and output.expanduser().resolve() != destination:
            content = (
                json.dumps(
                    document.model_dump(mode="json", exclude_none=True),
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n"
            )
            atomic_write_text(output, content, force=force)
    except (OSError, UnicodeError, ValidationError, ValueError) as exc:
        _abort(str(exc), code=2)
    _print_json(
        {
            "action": "document_ingested",
            "document_id": document.document_id,
            "format": document.manifest.format.value,
            "blocks": sum(len(page.blocks) for page in document.pages),
            "repository_path": str(destination),
            "output": str(output.expanduser().resolve()) if output else None,
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
            help="paper, evidence, package, document, draft, or evidence-span",
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
    }
    model = schema_models.get(kind)
    if model is None:
        _abort(
            "--kind must be paper, evidence, package, document, draft, or evidence-span",
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
