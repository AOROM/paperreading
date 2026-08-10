"""Validate the repository's installable Codex skill."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESOURCE_RE = re.compile(r"`((?:references|scripts|assets)/[^`\s]+)`")
PERSONAL_PATH_RE = re.compile(r"(?:[A-Za-z]:\\|/Users/|/home/[^/\s]+)")


def validate(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_dir = skill_dir.resolve()
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.is_file():
        return [f"Missing required file: {skill_md}"]

    try:
        content = skill_md.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return [f"SKILL.md is not valid UTF-8: {exc}"]

    match = FRONTMATTER_RE.match(content)
    if match is None:
        return ["SKILL.md must start with a closed YAML frontmatter block"]

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return [f"Invalid SKILL.md frontmatter: {exc}"]

    if not isinstance(frontmatter, dict):
        return ["SKILL.md frontmatter must be a YAML mapping"]

    expected_keys = {"name", "description"}
    actual_keys = set(frontmatter)
    if actual_keys != expected_keys:
        errors.append(
            "SKILL.md frontmatter keys must be exactly name and description; "
            f"found {sorted(actual_keys)}"
        )

    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not isinstance(name, str) or not SKILL_NAME_RE.fullmatch(name):
        errors.append("Skill name must use lowercase hyphen-case")
    elif len(name) > 64:
        errors.append("Skill name must not exceed 64 characters")
    elif skill_dir.name != name:
        errors.append(
            f"Skill folder '{skill_dir.name}' must match frontmatter name '{name}'"
        )

    if not isinstance(description, str) or not description.strip():
        errors.append("Skill description must be a non-empty string")
    elif len(description) > 1024:
        errors.append("Skill description must not exceed 1024 characters")
    elif "<" in description or ">" in description:
        errors.append("Skill description must not contain angle brackets")

    line_count = len(content.splitlines())
    if line_count > 500:
        errors.append(f"SKILL.md has {line_count} lines; keep it at or below 500")

    if (skill_dir / "README.md").exists():
        errors.append(
            "Keep repository documentation outside the installable skill folder"
        )

    body = content[match.end() :]
    for relative in sorted(set(RESOURCE_RE.findall(body))):
        if not (skill_dir / relative).is_file():
            errors.append(f"Referenced resource does not exist: {relative}")

    agent_yaml = skill_dir / "agents" / "openai.yaml"
    if not agent_yaml.is_file():
        errors.append("Missing recommended agents/openai.yaml")
    else:
        try:
            agent = yaml.safe_load(agent_yaml.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, yaml.YAMLError) as exc:
            errors.append(f"Invalid agents/openai.yaml: {exc}")
        else:
            interface = agent.get("interface") if isinstance(agent, dict) else None
            if not isinstance(interface, dict):
                errors.append("agents/openai.yaml must contain an interface mapping")
            else:
                short = interface.get("short_description", "")
                prompt = interface.get("default_prompt", "")
                if not isinstance(short, str) or not 25 <= len(short) <= 64:
                    errors.append(
                        "interface.short_description must contain 25-64 characters"
                    )
                if not isinstance(prompt, str) or f"${name}" not in prompt:
                    errors.append(
                        f"interface.default_prompt must explicitly mention ${name}"
                    )

    for path in skill_dir.rglob("*"):
        if (
            not path.is_file()
            or any(part in {".git", "__pycache__"} for part in path.parts)
            or path.suffix == ".pyc"
        ):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(
                f"Text resource is not valid UTF-8: {path.relative_to(skill_dir)}"
            )
            continue
        if PERSONAL_PATH_RE.search(text):
            errors.append(
                f"Personal absolute path found in {path.relative_to(skill_dir)}"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", type=Path)
    args = parser.parse_args()

    errors = validate(args.skill_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    file_count = sum(1 for path in args.skill_dir.rglob("*") if path.is_file())
    print(f"Skill is valid: {args.skill_dir.name} ({file_count} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
