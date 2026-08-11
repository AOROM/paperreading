# 贡献指南

[English](CONTRIBUTING.md) | **简体中文**

感谢改进 PaperReading。所有贡献都必须保持证据可追溯性、架构边界和向后兼容性。

## 项目契约

- 保持来源主张、报告证据和研究者判断可以相互区分。
- 保留不确定性和明确的零结果，不得用补造内容填充缺失信息。
- 只有识别证据充分时，才能把相关性表述强化为因果性表述。
- 文件修改必须经过验证、可以恢复，并由用户明确请求。
- 修改校验、投影或导出行为时，必须增加失败路径测试。
- 不得把规划中的能力描述为已经实现。

## 架构规则

允许的依赖方向为：

```text
domain <- validation / projections <- application interfaces / exporters
```

- `src/paperreading/domain/` 不得导入 Typer、OpenPyXL、AI SDK、Codex、Storage 或 Exporter。
- 工作簿专属逻辑只能放在 `src/paperreading/exporters/excel.py`。
- CLI 行为只能放在 `src/paperreading/cli.py`；可复用行为必须进入接口层之下。
- 将 `PaperRecord` 视为唯一核心模型，不得通过直接增加 Excel 列来修改 Domain 契约。
- 旧版工作簿变更必须通过 `to_legacy_13_fields` 实现，并保留兼容性测试。
- 保持 Codex 运行时 Skill 简洁。详细契约放入 references，确定性行为放入 Core。
- 不为路线图功能创建没有实现的空模块。

## Schema 变更

修改 `PaperRecord` 或 `EvidenceRef` 时：

1. 评估变更是否向后兼容。
2. 新增或更新模型测试与失败路径测试。
3. 运行 `python tools/export_schemas.py` 重新生成 Schema。
4. 更新合成示例和相关文档。
5. 在 `CHANGELOG.md` 中记录行为，并在 Pull Request 中说明迁移影响。

置信度评分规则必须保持确定性和可解释性。调用方提供的置信度不得绕过仓库规则。

## 变更范围与数据安全

- 运行时包代码放在 `src/paperreading/`。
- Codex 专属指令放在 `skills/papers-reading-skill/`。
- 测试、示例、Schema、Benchmark 和维护者文档保留在仓库层。
- 不提交受版权保护的论文正文、未获再分发授权的数据、个人工作簿、访问令牌、个人路径或其他敏感信息。
- 测试和示例必须使用合成材料。
- 修改期刊等级证据时，注明来源、体系、版本、生效边界和核验日期；不得推断不同评价体系之间的映射。

## 文档翻译

- 保持 `README.md` 与 `README.zh-CN.md` 语义一致。
- 保持 `CONTRIBUTING.md` 与 `CONTRIBUTING.zh-CN.md` 语义一致。
- 保持 `ROADMAP.md` 与 `ROADMAP.zh-CN.md` 语义一致。
- 两种语言中的命令、路径、标识符和行为契约必须相同；只翻译说明文字。

## 本地检查

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

工作簿变更必须覆盖正常追加、重复跳过、Schema 不匹配且源文件不变、备份创建，以及通过显式路径或配置解析目标。Core 变更应根据适用范围覆盖 Schema 拒绝、证据来源、因果语言边界、投影兼容与 Exporter 失败行为。

## Pull Request

在说明中写清：

1. 要解决的问题。
2. Core Schema、公开 Schema、投影或外部行为是否发生变化。
3. 执行过的验证命令及结果。
4. 涉及外部资料时的来源与版本。
5. 变更如何保持证据约束和安全输出行为。
6. 哪项路线图能力真正成为已实现功能（如适用）。
