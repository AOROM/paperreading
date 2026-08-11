# PaperReading 路线图

[English](ROADMAP.md) | **简体中文**

本路线图区分已经交付的行为与技术假说。只有公开契约、迁移或兼容行为、失败路径、测试和文档全部存在，一项能力才算完成。

## 已交付基础

### v0.2 — Research Intelligence Core

状态：已实现，并继续作为兼容性契约维护。

- 严格的 `PaperRecord` 与 `EvidenceRef` 模型。
- 确定性的来源位置具体度评分。
- 证据与因果语言校验。
- JSON、Markdown、旧版 13 字段与安全 Excel 输出。
- CLI、Python API、公开 Schema、合成示例与 CI 门禁。

### v0.3 — Schema Separation & Migration

状态：已在仓库中实现。

- 公开的 `PaperDocument`、`PaperDraft` 与 `PaperPackage` 模型。
- 严格分离来源约束记录与研究者分析。
- 使用 `EvidenceSpan` ID 构建稳定且去重的证据图。
- 确定性 v0.2 → v0.3 迁移，并显式保留溯源局限。
- UTF-8 文本与 Markdown 的确定性摄取，包含文本块与章节位置。
- 来源、页码、文本块、章节、引文和文本哈希核验。
- `.paperreading/` 下可检查的原子文件 Repository。
- 版本化 v0.2 / v0.3 JSON Schema 与确定性示例。
- 校验、CLI、JSON、Markdown、旧版投影与 Excel 的 v0.3 支持。
- 通过回归测试证明迁移包完整保持 v0.2 的 13 字段投影。

## 下一阶段：完成 Evidence Engine

状态：规划中，尚未实现。

完成标准：

- 在明确的 Adapter 边界后提供可选 PDF 解析器，并明确说明页面几何、表格和图形限制。
- 在 Provider 接口后实现多阶段提取协议；Domain 不依赖 Provider。
- 实现从 `PaperDraft` Candidate / Conflict 审阅到最终 `PaperPackage` 的流程。
- 支持 PDF 文本块、表格、图形和方程的证据核验，并保留类型化 Partial 状态。
- 发布允许再分发的小型 Golden Dataset，以及 Unsupported Claim、位置解析与因果语言指标。
- 记录可复现的 Prompt / Provider 元数据，但不保存密钥或受版权保护来源。

## v0.4 — Batch Research Library

状态：规划中，尚未实现。

- 支持恢复且按条目隔离失败的批量摄取。
- 在既有 Repository Port 后加入 SQLite 与版本化迁移。
- 按方法、变量、数据集、证据状态和标签搜索筛选。
- 确定性 Literature Matrix 与记录级比较溯源。
- 增量项目索引与可导出的运行报告。

## v0.5 — Evidence-Grounded Synthesis

状态：规划中，尚未实现。

- 跨已核验记录识别共识与冲突。
- 每项综合陈述绑定支持与反对它的论文 ID。
- 使用公开分类体系生成证据派生 Gap Candidate。
- 提供透明的可行性、新颖性和证据覆盖分项。
- 从已审阅 Gap 生成可执行研究设计，但绝不将其描述为来源发现。

## v0.6 — Empirical Method Auditors

状态：规划中，尚未实现。

- OLS 与面板固定效应检查。
- DID、分期 DID 与事件研究检查。
- IV 与 RDD 检查。
- PSM、安慰剂和机制解释检查。
- 方法专属样本、弃权行为与误报测试。

## v1.0 — Stable Ecosystem

状态：规划中，尚未实现。

- 稳定 Schema、弃用与迁移政策。
- PyPI 发布和签名发布产物。
- Provider、Parser、Repository 与 Exporter 插件入口。
- MCP、Zotero、BibTeX 和更多 Agent Adapter。
- 公开 PaperReading-Bench 方法与可复现基线。

## 跨版本不变量

1. 来源主张、报告证据与研究者分析始终保持分离。
2. 每项跨论文派生陈述都标识支持它的具体记录。
3. 因果表述不得强于识别证据。
4. 可追溯性和核验分数不得伪装成真实性或研究质量。
5. Domain 始终独立于 Interface、Provider、Storage 与 Exporter。
6. 旧版 Excel 兼容持续由成功路径和失败路径测试覆盖。
7. 规划功能不得被文档描述为已经交付。
