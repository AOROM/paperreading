# 贡献指南

[English](CONTRIBUTING.md) | **简体中文**

感谢改进 PaperReading。规范性[《学术研究底层逻辑》](RESEARCH_PRINCIPLES.zh-CN.md)约束所有贡献。当研究完整性与兼容性、便利性、性能或增长目标冲突时，以该原则为准。

## 项目契约

- 标明变更影响哪些原则编号（P1–P12），并说明实现如何执行这些原则。
- 保持来源主张、报告证据和研究者判断可以相互区分。
- 保留不确定性和明确的零结果，不得用补造内容填充缺失信息。
- 只有识别证据充分时，才能把相关性表述强化为因果性表述。
- 文件修改必须经过验证、可以恢复，并由用户明确请求。
- 修改校验、投影或导出行为时，必须增加失败路径测试。
- 不得把规划中的能力描述为已经实现。

## 架构规则

允许的依赖方向为：

```text
domain <- migrations / ingestion / verification / validation / projections
       <- application use cases <- CLI / Skill / exporters / repositories
```

- `src/paperreading/domain/` 不得导入 Typer、OpenPyXL、AI SDK、Codex、Storage 或 Exporter。
- 工作簿专属逻辑只能放在 `src/paperreading/exporters/excel.py`。
- CLI 行为只能放在 `src/paperreading/cli.py`；可复用编排进入 `application/`，可替换持久化必须位于 `repositories/base.py` 之后。
- 将 v0.3 `PaperPackage` 视为当前研究资产，并将 v0.2 `PaperRecord` 继续作为受支持的兼容契约。
- 来源派生字段只进入 `GroundedPaperRecord`；研究者或 AI 辅助解释必须进入 `ResearchAnalysis`。
- 旧版工作簿变更必须通过 `to_legacy_13_fields` 实现，并保留兼容性测试。
- 保持 Codex 运行时 Skill 简洁。详细契约放入 references，确定性行为放入 Core。
- 不为路线图功能创建没有实现的空模块。

## Schema 变更

修改公开 Domain 模型或证据契约时：

1. 判断变更在当前 Schema 版本内是否向后兼容。
2. 如果不兼容，引入新版本和显式确定性迁移，绝不静默重新解释旧 JSON。
3. 按适用范围增加模型、未解析引用、迁移、往返与失败路径测试。
4. 运行 `python tools/export_schemas.py` 重新生成 Schema，并运行 `python tools/generate_examples.py` 重新生成示例。
5. 保持 `schemas/v0.2/` 或 `schemas/v0.3/` 中的不可变契约；根目录 Schema 文件是已记录的别名。
6. 同步更新两种语言文档，并在 `CHANGELOG.md` 和 Pull Request 中说明迁移影响。

可追溯性与置信度规则必须保持确定性和可解释性。调用方提供的值不得绕过仓库规则。这些分数不得被描述为真实性、研究质量、因果有效性或外部效度。

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

## 贡献许可

PaperReading 依据 [MIT 许可证](LICENSE)分发。提交贡献即表示你确认自己有权贡献相关内容，并同意该贡献按同一许可证分发；如需其他安排，必须明确说明并获得维护者接受。

- 保留兼容第三方材料中的版权、署名与许可证声明。
- 不得提交许可条件与仓库分发不兼容的代码、文本、数据、图片或研究摘录。
- 在 Pull Request 中注明所引入外部材料的来源与许可证。
- 仓库的 MIT 许可证不会重新许可论文、数据集、用户输入、机密材料或生成摘录。

## 本地检查

```bash
python -m pip install -e ".[excel,dev]"
python -m ruff check .
python -m ruff format --check .
python -m mypy
python tools/export_schemas.py --check
python tools/generate_examples.py --check
python tools/validate_skill.py skills/papers-reading-skill
python tools/validate_license.py
python -m unittest discover -s tests -v
python -m pip wheel --no-deps --wheel-dir dist .
python tools/validate_license.py --wheel-dir dist
```

工作簿变更必须覆盖正常追加、重复跳过、Schema 不匹配且源文件不变、备份创建，以及通过显式路径或配置解析目标。Core 变更应根据适用范围覆盖 Schema 拒绝、未解析证据 ID、来源正文核验状态、因果语言边界、版本迁移、投影兼容与 Exporter 失败行为。

## Pull Request

在说明中写清：

1. 要解决的问题。
2. Core Schema、公开 Schema、投影或外部行为是否发生变化。
3. 执行过的验证命令及结果。
4. 涉及外部资料时的来源与版本。
5. 变更如何保持证据约束和安全输出行为。
6. 哪项路线图能力真正成为已实现功能（如适用）。
7. 影响哪些 Research Principles，以及仍然存在的权衡或局限。
8. 是否包含外部材料；如包含，说明其来源、许可证与再分发依据。
