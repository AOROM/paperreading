# Contributing

**English** | [简体中文](CONTRIBUTING.zh-CN.md)

Thank you for improving PaperReading. Contributions must preserve evidence traceability, architectural boundaries, and backward compatibility.

## Project contract

- Keep source claims, reported evidence, and researcher assessment distinguishable.
- Preserve uncertainty and explicit null results; never fill missing information with invented content.
- Require identification evidence before strengthening associative language into causal language.
- Keep file mutations validated, reversible, and explicitly requested by the user.
- Add failure-path tests when changing validation, projection, or export behavior.
- Do not document a planned capability as implemented.

## Architecture rules

The allowed dependency direction is:

```text
domain <- validation / projections <- application interfaces / exporters
```

- `src/paperreading/domain/` must not import Typer, OpenPyXL, an AI SDK, Codex, storage, or an exporter.
- Put workbook-specific logic only in `src/paperreading/exporters/excel.py`.
- Put CLI behavior only in `src/paperreading/cli.py`; reusable behavior belongs below the interface layer.
- Treat `PaperRecord` as the canonical model. Do not add an Excel column directly to the domain contract.
- Implement legacy workbook changes through `to_legacy_13_fields` and retain compatibility tests.
- Keep the Codex runtime Skill concise. Detailed contracts belong in its references, and deterministic behavior belongs in the Core.
- Do not create empty placeholder modules for roadmap features.

## Schema changes

When changing `PaperRecord` or `EvidenceRef`:

1. Assess whether the change is backward compatible.
2. Add or update model and failure-path tests.
3. Regenerate schemas with `python tools/export_schemas.py`.
4. Update the synthetic example and relevant documentation.
5. Record the behavior in `CHANGELOG.md` and describe migration impact in the pull request.

Confidence scoring rules must remain deterministic and explainable. A caller-supplied confidence value must never bypass repository rules.

## Scope and data safety

- Keep runtime package code under `src/paperreading/`.
- Keep Codex-specific instructions under `skills/papers-reading-skill/`.
- Keep tests, examples, schemas, benchmarks, and maintainer documentation at repository level.
- Do not commit copyrighted paper text, data without redistribution permission, personal workbooks, access tokens, personal filesystem paths, or other sensitive information.
- Use synthetic fixtures for tests and examples.
- When modifying journal-ranking evidence, document its source, system, version, effective boundary, and verification date. Never infer a mapping between ranking systems.

## Documentation translations

- Keep `README.md` and `README.zh-CN.md` semantically aligned.
- Keep `CONTRIBUTING.md` and `CONTRIBUTING.zh-CN.md` semantically aligned.
- Keep `ROADMAP.md` and `ROADMAP.zh-CN.md` semantically aligned.
- Keep commands, paths, identifiers, and behavioral contracts identical across languages; translate explanatory prose only.

## Local checks

```bash
python -m pip install -e ".[excel,dev]"
python -m ruff check .
python -m ruff format --check .
python -m mypy
python tools/export_schemas.py --check
python tools/validate_skill.py skills/papers-reading-skill
python -m unittest discover -s tests -v
python -m pip wheel --no-deps --wheel-dir dist .
```

Workbook changes must cover successful append, duplicate no-op, schema mismatch with unchanged source, backup creation, and explicit or configured destination resolution. Core changes must cover schema rejection, evidence provenance, causal-language boundaries, projection compatibility, and exporter failure behavior where applicable.

## Pull requests

State clearly:

1. The problem being solved.
2. Whether the Core schema, public schema, projection, or external behavior changes.
3. The validation commands run and their results.
4. The source and version of any external material.
5. How the change preserves evidence grounding and safe output behavior.
6. Which roadmap capability becomes genuinely implemented, if any.
