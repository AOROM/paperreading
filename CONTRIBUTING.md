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
domain <- migrations / ingestion / verification / validation / projections
       <- application use cases <- CLI / Skill / exporters / repositories
```

- `src/paperreading/domain/` must not import Typer, OpenPyXL, an AI SDK, Codex, storage, or an exporter.
- Put workbook-specific logic only in `src/paperreading/exporters/excel.py`.
- Put CLI behavior only in `src/paperreading/cli.py`; reusable orchestration belongs in `application/`, and replaceable persistence belongs behind `repositories/base.py`.
- Treat v0.3 `PaperPackage` as the current research asset. Preserve v0.2 `PaperRecord` as a supported compatibility contract.
- Keep source-derived fields in `GroundedPaperRecord`; researcher or AI-assisted interpretation belongs in `ResearchAnalysis`.
- Implement legacy workbook changes through `to_legacy_13_fields` and retain compatibility tests.
- Keep the Codex runtime Skill concise. Detailed contracts belong in its references, and deterministic behavior belongs in the Core.
- Do not create empty placeholder modules for roadmap features.

## Schema changes

When changing a public domain model or evidence contract:

1. Determine whether the change is backward compatible within its schema version.
2. If it is not, introduce a new version and an explicit deterministic migration; never reinterpret old JSON silently.
3. Add model, unresolved-reference, migration, round-trip, and failure-path tests as applicable.
4. Regenerate schemas with `python tools/export_schemas.py` and examples with `python tools/generate_examples.py`.
5. Preserve immutable contracts under `schemas/v0.2/` or `schemas/v0.3/`; root schema files are documented aliases.
6. Update both documentation languages and record migration impact in `CHANGELOG.md` and the pull request.

Traceability and confidence rules must remain deterministic and explainable. A caller-supplied value must never bypass repository rules. These scores must not be described as truth, study quality, causal validity, or external validity.

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
python tools/generate_examples.py --check
python tools/validate_skill.py skills/papers-reading-skill
python -m unittest discover -s tests -v
python -m pip wheel --no-deps --wheel-dir dist .
```

Workbook changes must cover successful append, duplicate no-op, schema mismatch with unchanged source, backup creation, and explicit or configured destination resolution. Core changes must cover schema rejection, unresolved evidence IDs, source-content verification states, causal-language boundaries, version migration, projection compatibility, and exporter failure behavior where applicable.

## Pull requests

State clearly:

1. The problem being solved.
2. Whether the Core schema, public schema, projection, or external behavior changes.
3. The validation commands run and their results.
4. The source and version of any external material.
5. How the change preserves evidence grounding and safe output behavior.
6. Which roadmap capability becomes genuinely implemented, if any.
