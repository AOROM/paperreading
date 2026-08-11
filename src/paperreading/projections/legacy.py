"""Backward-compatible projection to the original 13-column workbook."""

from __future__ import annotations

from collections.abc import Iterable

from paperreading.domain import PaperRecord, Variable, VariableRole

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


def _variables_by_role(record: PaperRecord, roles: set[VariableRole]) -> str:
    return "；".join(
        _variable_text(variable)
        for variable in record.variables
        if variable.role in roles
    )


def to_legacy_13_fields(record: PaperRecord) -> dict[str, str]:
    """Project a PaperRecord without making the legacy schema the domain model."""

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
        record, {VariableRole.DEPENDENT, VariableRole.INDEPENDENT}
    )
    if core_variables:
        data_lines.append(f"【核心变量】{core_variables}")
    mechanism_variables = _variables_by_role(
        record, {VariableRole.MEDIATOR, VariableRole.MODERATOR}
    )
    if mechanism_variables:
        data_lines.append(f"【机制变量】{mechanism_variables}")
    controls = _variables_by_role(record, {VariableRole.CONTROL})
    if controls:
        data_lines.append(f"【控制变量】{controls}")

    extensions = []
    for extension in record.extensions:
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
