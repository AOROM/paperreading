"""Backward-compatible projection to the original 13-column workbook."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from paperreading.domain import (
    AnalyzedResearchExtension,
    GroundedPaperRecord,
    PaperPackage,
    PaperRecord,
    ResearchExtension,
    Variable,
    VariableRole,
)

LEGACY_FIELDS = [
    "序号",
    "论文名称",
    "作者",
    "期刊",
    "期刊等级",
    "发表时间",
    "关键词",
    "研究问题",
    "研究结论",
    "研究逻辑",
    "实证模型",
    "数据来源和变量设置",
    "可进一步延伸的研究设计",
]


def _numbered(items: Iterable[str]) -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(items, start=1))


def _variable_text(variable: Variable) -> str:
    name = variable.name
    if variable.abbreviation:
        name = f"{name}（{variable.abbreviation}）"
    details = [item for item in (variable.definition, variable.measurement) if item]
    return f"{name}：{'；'.join(details)}" if details else name


def _variables_by_role(variables: list[Variable], roles: set[VariableRole]) -> str:
    return "；".join(
        _variable_text(variable) for variable in variables if variable.role in roles
    )


def to_legacy_13_fields(artifact: PaperRecord | PaperPackage) -> dict[str, str]:
    """Project v0.2 or v0.3 without making the legacy schema the domain model.

    A v0.3 package deliberately keeps researcher-authored extensions outside the
    source-grounded record.  The legacy workbook requires that thirteenth field,
    so packages without at least one extension cannot be projected safely.
    """

    record: PaperRecord | GroundedPaperRecord
    extensions_source: Sequence[ResearchExtension | AnalyzedResearchExtension]
    if isinstance(artifact, PaperPackage):
        record = artifact.record
        if not artifact.analysis or not artifact.analysis.research_extensions:
            raise ValueError(
                "legacy 13-field projection requires at least one research "
                "extension in package.analysis.research_extensions"
            )
        extensions_source = artifact.analysis.research_extensions
    else:
        record = artifact
        extensions_source = artifact.extensions

    metadata = record.metadata
    design = record.empirical_design

    conclusion_lines = [
        f"【基准结论】{finding.statement}" for finding in record.findings
    ]
    conclusion_lines.extend(
        f"【作用机制】{mechanism.statement}" for mechanism in record.mechanisms
    )
    conclusion_lines.extend(
        f"【异质性】{finding.statement}" for finding in record.heterogeneity
    )

    if design is None:
        model_lines = ["【基准模型】不适用（非实证研究）"]
    else:
        baseline_parts = [f"方法：{design.method}"]
        if design.model_equation:
            baseline_parts.append(f"方程：{design.model_equation}")
        if design.fixed_effects:
            baseline_parts.append(f"固定效应：{'、'.join(design.fixed_effects)}")
        if design.standard_errors:
            baseline_parts.append(f"标准误：{design.standard_errors}")
        if design.identification_strategy:
            baseline_parts.append(f"识别：{design.identification_strategy}")
        model_lines = [f"【基准模型】{'；'.join(baseline_parts)}"]
        if design.endogeneity_methods:
            model_lines.append(f"【内生性】{'；'.join(design.endogeneity_methods)}")
        if design.robustness_checks or record.robustness:
            checks = [*design.robustness_checks]
            checks.extend(test.name for test in record.robustness)
            model_lines.append(f"【稳健性】{'；'.join(checks)}")

    sample_parts = [item for item in (record.data.sample, record.data.period) if item]
    data_lines = [f"【样本】{'；'.join(sample_parts)}"] if sample_parts else []
    if record.data.sources:
        data_lines.append(f"【数据】{'；'.join(record.data.sources)}")
    core_variables = _variables_by_role(
        record.variables, {VariableRole.DEPENDENT, VariableRole.INDEPENDENT}
    )
    if core_variables:
        data_lines.append(f"【核心变量】{core_variables}")
    mechanism_variables = _variables_by_role(
        record.variables, {VariableRole.MEDIATOR, VariableRole.MODERATOR}
    )
    if mechanism_variables:
        data_lines.append(f"【机制变量】{mechanism_variables}")
    controls = _variables_by_role(record.variables, {VariableRole.CONTROL})
    if controls:
        data_lines.append(f"【控制变量】{controls}")

    extensions = []
    for extension in extensions_source:
        parts = [f"【{extension.title}】{extension.research_question}"]
        if extension.identification_strategy:
            parts.append(f"识别：{extension.identification_strategy}")
        if extension.data_sources:
            parts.append(f"数据：{'、'.join(extension.data_sources)}")
        if extension.falsification:
            parts.append(f"证伪：{extension.falsification}")
        extensions.append("；".join(parts))

    return {
        "论文名称": metadata.title,
        "作者": "，".join(metadata.authors),
        "期刊": metadata.journal or "",
        "期刊等级": "，".join(item.label for item in metadata.rankings),
        "发表时间": metadata.publication_date or "",
        "关键词": "；".join(metadata.keywords),
        "研究问题": _numbered(record.research_questions),
        "研究结论": "\n".join(conclusion_lines),
        "研究逻辑": record.theoretical_framework.causal_chain or "",
        "实证模型": "\n".join(model_lines),
        "数据来源和变量设置": "\n".join(data_lines),
        "可进一步延伸的研究设计": _numbered(extensions),
    }
