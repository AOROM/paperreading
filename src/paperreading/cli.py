"""Command-line interface for the PaperReading Core."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, NoReturn

import typer
from pydantic import ValidationError

from paperreading import __version__
from paperreading.domain import EvidenceRef, PaperRecord
from paperreading.exporters import ExportFormat, JsonExporter, MarkdownExporter
from paperreading.exporters.text import atomic_write_text
from paperreading.projections import to_legacy_13_fields
from paperreading.validation import validate_record

app = typer.Typer(
    name="paperreading",
    help="Evidence-grounded research intelligence from structured paper records.",
    no_args_is_help=True,
    add_completion=False,
)


def _load_record(path: Path) -> PaperRecord:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return PaperRecord.model_validate(payload)


def _abort(message: str, *, code: int = 1) -> NoReturn:
    typer.echo(
        json.dumps({"action": "error", "message": message}, ensure_ascii=False),
        err=True,
    )
    raise typer.Exit(code)


def _print_json(payload: object) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


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
    """Create a minimal local .paperreading project without a database."""

    state_dir = directory.expanduser().resolve() / ".paperreading"
    config = state_dir / "config.toml"
    content = (
        '[general]\nlanguage = "zh-CN"\n\n'
        '[output]\ndefault_format = "markdown"\n\n'
        "[evidence]\nrequire_locator = true\n\n"
        '[excel]\nsheet_zh = "中文"\nsheet_en = "英文"\n'
    )
    try:
        state_dir.mkdir(parents=True, exist_ok=True)
        (state_dir / "papers").mkdir(exist_ok=True)
        atomic_write_text(config, content, force=force)
    except Exception as exc:
        _abort(str(exc))
    _print_json(
        {
            "action": "project_initialized",
            "directory": str(state_dir),
            "config": str(config),
        }
    )


@app.command()
def validate(
    record: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    strict: Annotated[
        bool,
        typer.Option(
            "--strict",
            help="Treat evidence without structural locators as invalid.",
        ),
    ] = False,
) -> None:
    """Validate schema, evidence traceability, and causal language."""

    try:
        paper = _load_record(record)
        report = validate_record(paper, strict=strict)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        _abort(str(exc), code=2)
    _print_json(report.model_dump(mode="json"))
    if not report.valid:
        raise typer.Exit(2)


@app.command()
def project(
    record: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    """Project a rich PaperRecord to the legacy 13-field JSON contract."""

    try:
        paper = _load_record(record)
        payload = to_legacy_13_fields(paper)
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
    record: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    destination: Annotated[Path, typer.Argument()],
    format: Annotated[ExportFormat, typer.Option("--format", "-f")] = ExportFormat.JSON,
    sheet: Annotated[str, typer.Option("--sheet")] = "中文",
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    """Export one validated record to JSON, Markdown, or a legacy Excel workbook."""

    try:
        paper = _load_record(record)
        report = validate_record(paper)
        if not report.valid:
            _abort(
                "record failed evidence or causal-language validation",
                code=2,
            )

        if format is ExportFormat.JSON:
            result = JsonExporter().export([paper], destination, force=force)
        elif format is ExportFormat.MARKDOWN:
            result = MarkdownExporter().export([paper], destination, force=force)
        else:
            try:
                from paperreading.exporters.excel import ExcelExporter
            except ModuleNotFoundError:
                _abort(
                    "Excel support is not installed; install paperreading[excel].",
                    code=2,
                )
            result = ExcelExporter().export([paper], destination, sheet=sheet)
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        _abort(str(exc), code=2)
    _print_json(result)


@app.command()
def schema(
    kind: Annotated[str, typer.Option("--kind", help="paper or evidence")] = "paper",
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    """Print or save the machine-readable JSON Schema."""

    if kind == "paper":
        payload = PaperRecord.model_json_schema()
    elif kind == "evidence":
        payload = EvidenceRef.model_json_schema()
    else:
        _abort("--kind must be paper or evidence", code=2)
    content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
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
