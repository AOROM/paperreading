# PaperReading 路线图

[English](ROADMAP.md) | **简体中文**

本路线图区分已经交付的行为与尚待验证的技术假说。只有公开契约、失败行为、测试和文档均已具备时，里程碑才算完成。

## v0.2 — Core Refactor

状态：已在仓库中实现。

- 规范化 Pydantic `PaperRecord` 与 `EvidenceRef` 模型。
- 确定性的证据置信度评分。
- 证据和因果语言校验。
- 旧版 13 字段投影。
- JSON、Markdown 与安全 Excel Exporter。
- `paperreading` CLI 和可导入的 Python API。
- 公开 JSON Schema 与合成示例记录。
- Codex Skill 作为 Core 的 Adapter。
- CI 中的 lint、类型、Schema、构建、Skill 与兼容性门禁。

## v0.3 — Evidence Engine

状态：规划中。

- 章节感知的 PDF 文档模型和可选解析依赖。
- 具有显式 Provider 接口的多阶段提取协议。
- Claim-to-Evidence Graph 与证据去重。
- 将提取一致性和交叉核验纳入置信度评分。
- 扩展因果语言 Benchmark 和 Unsupported Claim 指标。
- 第一组规模较小且允许再分发的 Golden Dataset。

## v0.4 — Batch Research Library

状态：规划中。

- 支持失败恢复的批量摄取。
- 本地 SQLite Repository 与版本化迁移。
- 按方法、变量、数据集和标签进行搜索与筛选。
- Literature Matrix、确定性比较和记录级溯源。
- `.paperreading/` 中的增量项目索引。

## v0.5 — Research Intelligence

状态：规划中。

- 跨记录的共识与冲突检测。
- 每项综合结论绑定支持和反对该结论的论文 ID。
- 使用公开分类体系计算证据驱动的 Gap Candidate。
- 使用透明分项评估可行性和新颖性。
- 从验证后的 Gap 推导可执行研究设计。

## v0.6 — Empirical Method Auditors

状态：规划中。

- OLS 与面板固定效应检查。
- DID、分期 DID 与事件研究检查。
- IV 与 RDD 检查。
- PSM、安慰剂和中介机制解释检查。
- 方法专属测试样本与误报测试。

## v1.0 — Stable Ecosystem

状态：规划中。

- 稳定 Schema 与迁移政策。
- PyPI 发布和签名发布产物。
- Provider 与 Exporter 插件入口。
- MCP、Zotero、BibTeX 和更多 Agent Adapter。
- 公开 PaperReading-Bench 方法与基准结果。

## 所有版本共同遵守的不变量

1. 来源主张、报告证据与研究者判断始终保持分离。
2. 每项跨论文派生陈述都必须标识支持它的具体记录。
3. 因果表述不得强于识别证据。
4. Domain 层始终独立于 Interface、Provider 与 Exporter。
5. 旧版 Excel 兼容性持续由失败路径测试覆盖。
6. 规划中的功能不得被文档描述为已经实现。
