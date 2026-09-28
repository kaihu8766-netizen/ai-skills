# CHANGELOG

按日期倒序，一句话说明动机。

## 2026-09-28

- **v2 通用化改造（dual-agent-collab）**：从"企业级评审门禁"泛化为"通用双 Agent 协作"——新增任务路由表（重大/功能/搜索/琐事分级讨论与复核强度）、联网取证流程（references/research.md：事实点拆解、来源 S/A/B/C 分级、交叉验证、引用格式）、轻量档案（references/light-archive.md：无仓库自动存主 Agent 工作区）；门禁降级为可选高级模式（gates.md 显式 fail-closed 声明）；SKILL.md 重写为通用路由版（附简历快速开始示例）
- 新增技能 `dual-agent-collab`：双 Agent 协作评审工作流（事前对齐/事后复核/RV 档案/决策记录/定期自检/门禁规则）
- 建立治理规则 `GOVERNANCE.md`：技能单元定义、变更分级表、单仓软阈值、版本策略、与 project-trace 边界、安全红线
- 技能仓建仓（私有，kaihu8766-netizen/ai-skills）

## 评审记录

- RV-20260928-07：技能补丁 C（评审强制框架 + 通用门禁三件套），adopted
- RV-20260928-09：v2 通用化设计讨论（4 条件全落地），adopted
