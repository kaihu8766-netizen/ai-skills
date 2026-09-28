---
name: dual-agent-collab
description: 双 Agent 协作评审工作流（主执行 Agent + DeepSeek 独立评审 + 人类最终裁决）。覆盖事前对齐、事后复核、评审档案、决策记录、问题闭环与定期自检。当用户要求重大改动先与外部 AI 讨论再动手、完成后必须复核、全过程可溯源（企业级留痕）、或要求把评审当作强制门禁时使用；适用于代码、文档、设计、方案等任意项目，需配置 DeepSeek API key 与评审工作区。
---

# 双 Agent 协作模式

将"执行 Agent + DeepSeek 独立评审 + 人类最终裁决"固化为可复用工作流，保证：**事前对齐、事后复核、机器强制、全过程可溯源**。

## 角色与职责

| 角色 | 职责 |
|---|---|
| 主 Agent（本 Agent） | 执行任务；发起事前对齐与事后复核；维护档案 |
| DeepSeek（评审 Agent） | 独立评审（不参与执行，避免自我确认偏差）；给出通过/拒绝结论与改进意见 |
| 人类 | 最终裁决；拍板重大决策；评估收益 |

## 何时使用

- 任何"重大 / 功能级 / 不可逆"改动动手前（事前对齐）
- 任何改动完成、准备提交/发布前（事后复核）
- 用户要求全过程可溯源（企业级留痕）的项目
- 用户明确要求与 DeepSeek（或其他外部 AI）协作讨论

## 哪些改动必须评审（判定表）

| 改动类型 | 事前对齐（scheme） | 事后复核（review） |
|---|---|---|
| 红线文件/核心逻辑（代码、规则、脚本、配置） | 必须 | 必须 |
| 功能级新增/变更 | 必须 | 必须 |
| 非功能小改动（文案、样式、纯排版，≤3 文件/≤30 行） | 可走轻量通道（gates.md） | 引用已批准 RV |
| 纯只读检查/查询 | 不评审 | 不评审（结果落档即可） |
| 不可逆动作（删除、发布、外发、改权限） | 必须 | 必须；且人不在时 BLOCKED 上报 |

## 核心流程（每个周期走完 5 步）

1. **事前对齐（scheme 通道）**：动手前把方案（目标、改动点、风险、验收）发给 DeepSeek 评审 → 通过/有条件通过才动手，否则先改方案
2. **执行**：主 Agent 实现（小的非功能改动可走轻量通道，见 gates.md）
3. **事后复核（review 通道）**：完成后再发 DeepSeek 评审 → 通过才提交/发布；拒绝则修复后重审
4. **落档案**：评审编号、索引、原始 JSON、结论、决策记录（DECISIONS）、问题清单（OPEN_ISSUES/TODO 双向核销）
5. **定期自检**：按周期硬检查档案一致性与积压，增量收集问题；有变化/异常先与 DeepSeek 讨论再行动（讨论闸门，见 gates.md）

## 评审编号与档案（可溯源核心）

**三个 ID 必须分清**（实战中三者不同源，混用是常见事故源）：
- **RV-ID**：评审档案的唯一标识 `RV-YYYYMMDD-NN`（NN 为**当日序号**，如 RV-20260928-03）。写在档案 frontmatter `id:` 与索引"主题"列
- **索引序号**：台账行号（# 列），**每日/全表递增**——`adopt` 会追加新行，因此**索引序号 ≠ RV 号**。真实反例：RV-20260927-231 对应索引序号 232
- **GATE-ID**：门禁动作记录 `GATE-YYYYMMDD-NN`（提交闸门拦截时生成，另见 gates.md）

- 档案目录（默认）：`<工作区>/dual-agent/reviews/`，结构见 archive-format.md
- 每次评审必须落盘：原始请求/响应 JSON + 索引行（含状态），供事后审计
- 提交信息引用 RV 时，门禁按"日期-RV号"前缀（如 `2026-09-28-03-`）在索引中定位，**不是按序号**——索引行必须包含该前缀（通常落在档案文件名列）

## 快速开始

```bash
# 事前对齐（动手前）
DEEPSEEK_API_KEY=<key> python3 scripts/deepseek_review.py \
  --phase scheme --feature F-001 \
  --topic "RV-20260928-01-XX方案事前对齐" \
  --prompt "【方案评审】目标/改动点/风险/验收：...。请评审可行性与优先级，结论：通过/有条件通过/拒绝。" \
  --max-tokens 2500

# 事后复核（完成后）
DEEPSEEK_API_KEY=<key> python3 scripts/deepseek_review.py \
  --phase review \
  --topic "RV-20260928-02-XX完成复核" \
  --prompt "【完成复核】已完成内容：...。请独立评审：1) 是否符合事前对齐方案 2) 有无缺陷 3) 改进意见。结论：通过/拒绝。" \
  --max-tokens 2500
```

- `--force`：同一 topic 重审时跳过"已存在"检查
- 结论必须为：`通过` / `有条件通过`（列出条件）/ `拒绝`（列出原因）
- 有条件通过 = 按条件修复后补一次轻量复核或由主 Agent 逐条说明如何满足

**脚本定位（重要，防误用）**：`scripts/deepseek_review.py` 是**通用最小版**——只做"调用 DeepSeek + 原始 JSON 落盘 + 追加索引行"。项目级能力（双 hash 校验、.md 档案生成、evtools 只读证据、敏感词通道、多轮历史压缩、`--light`）**不在通用脚本内**，由使用方按 archive-format.md / gates.md 扩展接入（参考实现：project-trace/agent-communication-demo/deepseek_gate.py）。

## 决策与收益评估

- 重大决策（用户拍板）记录到 `DECISIONS.md`：决策号、背景、选项、选择、理由
- **收益评估前置**：向用户提出待拍板选项时，主 Agent **同步附上每个选项的收益/影响评估**（影响、成本、风险、替代方案），评估放在拍板之前而非拍板之后

## 详细参考

- [references/channels.md](references/channels.md)：评审通道参数、prompt 模板、结论词表
- [references/archive-format.md](references/archive-format.md)：档案目录结构、索引格式、DECISIONS/TODO/OPEN_ISSUES 规范
- [references/gates.md](references/gates.md)：Git 提交门禁（commit-msg 钩子三闸门）与讨论闸门规则（定时任务/周期自检触发条件）
