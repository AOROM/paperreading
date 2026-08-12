"""Validate repository and distribution licensing contracts."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]
LICENSE_PATH = ROOT / "LICENSE"
SKILL_LICENSE_PATH = ROOT / "skills" / "papers-reading-skill" / "LICENSE"
EXPECTED_EXPRESSION = "MIT"
EXPECTED_COPYRIGHT = "Copyright (c) 2026 AOROM"
REQUIRED_LICENSE_TEXT = (
    "MIT License",
    EXPECTED_COPYRIGHT,
    "Permission is hereby granted, free of charge, to any person obtaining a copy",
    "The above copyright notice and this permission notice shall be included",
    'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND',
)


def validate_source() -> list[str]:
    errors: list[str] = []
    if not LICENSE_PATH.is_file():
        return ["Missing root LICENSE file"]

    try:
        license_text = LICENSE_PATH.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return [f"LICENSE is not valid UTF-8: {exc}"]

    for required in REQUIRED_LICENSE_TEXT:
        if required not in license_text:
            errors.append(f"LICENSE is missing canonical MIT text: {required}")

    if not SKILL_LICENSE_PATH.is_file():
        errors.append("Standalone Codex Skill must include its own LICENSE")
    elif SKILL_LICENSE_PATH.read_text(encoding="utf-8") != license_text:
        errors.append("Codex Skill LICENSE must match the repository LICENSE")

    pyproject_path = ROOT / "pyproject.toml"
    with pyproject_path.open("rb") as stream:
        project = tomllib.load(stream)["project"]

    if project.get("license") != EXPECTED_EXPRESSION:
        errors.append('pyproject.toml must declare license = "MIT"')
    if project.get("license-files") != ["LICENSE"]:
        errors.append('pyproject.toml must declare license-files = ["LICENSE"]')

    documentation_contracts = {
        "README.md": "[MIT License](LICENSE)",
        "README.zh-CN.md": "[MIT 许可证](LICENSE)",
        "CONTRIBUTING.md": "MIT License",
        "CONTRIBUTING.zh-CN.md": "MIT 许可证",
    }
    for relative, marker in documentation_contracts.items():
        content = (ROOT / relative).read_text(encoding="utf-8")
        if marker not in content:
            errors.append(f"{relative} must contain the licensing marker: {marker}")

    return errors


def validate_wheel(wheel_dir: Path) -> list[str]:
    wheels = sorted(
        wheel_dir.glob("paperreading-*.whl"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not wheels:
        return [f"No PaperReading wheel found in {wheel_dir}"]

    expected_text = LICENSE_PATH.read_text(encoding="utf-8")
    wheel = wheels[0]
    errors: list[str] = []
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        license_names = [
            name for name in names if name.endswith(".dist-info/licenses/LICENSE")
        ]
        metadata_names = [
            name for name in names if name.endswith(".dist-info/METADATA")
        ]
        if len(license_names) != 1:
            errors.append("Wheel must contain exactly one dist-info/licenses/LICENSE")
        elif archive.read(license_names[0]).decode("utf-8") != expected_text:
            errors.append("Wheel LICENSE does not match the repository LICENSE")

        if len(metadata_names) != 1:
            errors.append("Wheel must contain exactly one dist-info/METADATA")
        else:
            metadata = archive.read(metadata_names[0]).decode("utf-8")
            if "License-Expression: MIT" not in metadata:
                errors.append("Wheel metadata must contain License-Expression: MIT")
            if "License-File: LICENSE" not in metadata:
                errors.append("Wheel metadata must contain License-File: LICENSE")

    if not errors:
        print(f"Wheel licensing is valid: {wheel.name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--wheel-dir",
        type=Path,
        help="Also validate the newest PaperReading wheel in this directory.",
    )
    args = parser.parse_args()

    errors = validate_source()
    if args.wheel_dir is not None and not errors:
        errors.extend(validate_wheel(args.wheel_dir))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Repository licensing is valid: MIT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
