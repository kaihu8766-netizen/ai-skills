# 档案规范（archive-format.md）

档案是"全过程可溯源"的落地。目录默认 `<工作区>/dual-agent/reviews/`（可用 `--out-dir` 覆盖），结构：

```text
dual-agent/
└── reviews/
    ├── 索引.md            # 全部评审的台账（一行一条，机器可解析）
    ├── raw/               # 每次评审的原始请求/响应 JSON（审计证据）
    └── <ymd>-<nn>-<topic>.md   # 归档总结（可选；评审结论要点）
```

## 索引行格式（追加式，不覆盖历史）

```markdown
| 序号 | YYYY-MM-DD | RV-YYYYMMDD-NN-主题 | 见档案（<ymd>-<nn>-RV-<topic>.md） | <状态> | <档案文件名> | 见档案 |
```

- **状态词**（新表）：`pending`（已发起）/ `adopted`（已批准）/ `rejected`（已拒绝）/ `closed`（已关闭归档）
- **门禁校验是带空格的精确子串** `"| adopted |"`——索引行状态列必须保持该格式（`| adopted |` 前后各一空格）；历史行可能混用旧词表（`✅ 全采纳 / 🔶 部分采纳 / ❌ 未采纳`），被门禁引用前需统一为新格式
- **只追加、不删历史行**；状态变更用新行表达（保持审计可追溯）

## 评审档案（.md）frontmatter 完整字段

生成评审档案时按以下字段集落盘（门禁按文件名前缀定位、按 `status` 校验，字段缺失会被拒收）：

```yaml
id: RV-YYYYMMDD-NN            # 评审 ID（与 topic 一致）
date: YYYY-MM-DDTHH:MM:SS
topic: RV-YYYYMMDD-NN-主题
status: pending | adopted | rejected | closed
diff_hash: <被评审仓 staged 文件 hash>          # 双 hash 之一：评审对象侧
project_trace_diff_hash: <档案仓 hash>          # 双 hash 之二：溯源仓侧（评审产物本身不进 hash）
decision_ids: []              # 关联决策 D-xxx
issue_ids: []                 # 关联问题 ISS-xxx
task_ids: []                  # 关联待办 T-xxx
phase: scheme | review
feature: F-xxx | null
commits: []
decision_maker: 用户           # 最终裁决人
reviewers: [DeepSeek]
model: deepseek-chat
raw_file: agent-communication-demo/raw/rv-<...>.json   # 原始请求/响应
raw_hash: <raw json hash>
supersedes: null
superseded_by: null
provenance: live | backfill    # live=实时评审；backfill=事后补录
```

正文包含：评审问题、DeepSeek 结论（原文节选）、采纳状态与决策人。

## 编号体系（三 ID 分离，勿混用）

| 编号 | 用途 | 格式 |
|---|---|---|
| RV-ID | 评审档案 ID | `RV-YYYYMMDD-NN`（NN=当日序号；≠索引序号） |
| 索引序号 | 台账行号 | 全表递增（adopt 追加新行会 +1，导致 ≠ RV 号） |
| GATE-ID | 门禁动作记录 | `GATE-YYYYMMDD-NN` |
| F | 方案/feature | `F-xxx`（scheme 通道必填） |
| D | 决策 | `D-NNN` |
| T | 待办 | `T-0NN`（TODO 表） |
| ISS | 问题 | `ISS-NNN`（OPEN_ISSUES 表） |

## 关键台账（同目录或工作区根）

- `DECISIONS.md`：重大决策记录——决策号、背景、选项对比、选择、理由、**收益评估**（待拍板选项附带：列出选项时每个选项同步附收益/影响评估，评估放在拍板之前）
- `TODO.md`：待办清单（待办→进行中→待拍板→已完成）；完成项双向核销 OPEN_ISSUES 对应项
- `OPEN_ISSUES.md`：未决问题（问题号、描述、优先级、状态、关联 RV/T）
- `DailySummary/YYYY-MM-DD.md`：定期自检结果（硬检查 + 问题清单 + DeepSeek 意见 + 待拍板项）

## 定期自检（周期任务）

1. **硬检查**：档案一致性（脚本测试）、RV 积压（pending 超阈值）、台账完整性（索引/决策/问题/TODO 存在且格式合法）
2. **增量收集**：自上次基线以来新增的 rejected/pending/反复轮评审、新增/到期问题、成本超阈值项
3. **讨论闸门**（gates.md）：硬检查异常或增量问题非空 → **必须**先与 DeepSeek 讨论并落盘 → 再行动；不可逆动作讨论不可得时 **BLOCKED 上报用户**，禁止擅自执行

## 红线（数据安全）

- 真实个人信息（发票、密钥、手机号、身份证等）**绝不进入任何公开仓库/档案**；需引用时脱敏（`9××××…××67` 式）
- API key 只走环境变量/本地配置，不写进脚本、提交或档案
- 敏感资产放 `private/` 目录并 gitignore，或留在本机不入库
