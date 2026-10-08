# CHANGELOG

按日期倒序，一句话说明动机。

## 2026-09-29

- **v2.1 降级门禁升级（dual-agent-collab）**：修复"静默降级"缺陷（无 DeepSeek key 时未询问即降级为子代理）。核心：SKILL.md 新增第 0 步「环境检查与降级门禁」（无 key 必须先单独询问用户并等待裁决，A 提供 key / B 同意降级 / C 跳过；重大/不可逆/对外交付类不可选 B，无独立复核 BLOCKED；路由归属明确功能性工作不得归 C；分类争议 fail-closed）；review-framework.md 新增「独立复核判据 5 条」（子代理=degraded 不算独立复核，硬门只认受控通道 RV 档案）+ 自证清白反制；light-archive.md 新增「降级记录」字段（status=degraded + 用户同意 + 硬门口径）；deepseek_review.py 补哈希留痕（raw prompt_hash/response_hash + 索引行 hash，防落盘后改写）；deps.md 补 key 三类注入入口；新增 references/env-check.md（1 分钟环境自检）。DeepSeek 终审 RV-20260929-07 adopted。

## 2026-09-29

- **v2.2 讨论触发机制修复（dual-agent-collab）**：修复"别的对话框加载技能后不知道要讨论"（v2.1 遗留：description 触发条件全为用户显式要求 + 无开工判定仪式，不讨论是默认行为而非显式违约）。核心：description 改为档位语义默认触发（凡可能产出交付物的任务动手前先按路由表判定）；新增核心流程第 0 步「开工三问·任务路由判定」（先显式输出判定行：任务类型=…、事前讨论=要/不要、事后复核=要/不要、理由=…，不讨论变成可被当场抓到的违约；判定行落档案不得自我放宽到跳过档，fail-closed）；light-archive.md 补「路由判定」字段；env-check.md 新增第 6 项「开工三问触发」自检（新会话不自知=FAIL）。DeepSeek 终审 RV-20260929-10 adopted。

## 2026-09-28

- **v2 通用化改造（dual-agent-collab）**：从"企业级评审门禁"泛化为"通用双 Agent 协作"——新增任务路由表（重大/功能/搜索/琐事分级讨论与复核强度）、联网取证流程（references/research.md：事实点拆解、来源 S/A/B/C 分级、交叉验证、引用格式）、轻量档案（references/light-archive.md：无仓库自动存主 Agent 工作区）；门禁降级为可选高级模式（gates.md 显式 fail-closed 声明）；SKILL.md 重写为通用路由版（附简历快速开始示例）
- 新增技能 `dual-agent-collab`：双 Agent 协作评审工作流（事前对齐/事后复核/RV 档案/决策记录/定期自检/门禁规则）
- 建立治理规则 `GOVERNANCE.md`：技能单元定义、变更分级表、单仓软阈值、版本策略、与 project-trace 边界、安全红线
- 技能仓建仓（私有，kaihu8766-netizen/ai-skills）

## 评审记录

- RV-20260928-07：技能补丁 C（评审强制框架 + 通用门禁三件套），adopted
- RV-20260928-09：v2 通用化设计讨论（4 条件全落地），adopted

## 2026-10-09

- **v2.4 细节补全（dual-agent-collab）**：review-framework.md 新增「五、有条件通过的完整闭环（条件闭合评审链）」（拆解条件→逐条落实→回标 adopted+adopted_at→闭合复核→链式记录，含常见失败模式）与「六、拒绝处理（评审反复拒绝时怎么办）」（拒绝分级表：真问题/证据不足/口径分歧/条件未落实/误判五类对策；防死锁规则：重审=新编号、评审对象=提交对象、1-2 轮无进展转人裁决、不修改历史；经验：90% 反复拒绝是真问题）；SKILL.md 版本号升至 v2.4。仓转 public（2026-10-09）。

## 2026-10-09（v2.5）

- **gates.md 补三条实战教训（从 invoice-precheck 项目 scheme 闸门 bug 提炼）**：①跨仓共用引擎的死路径（闸门不显式传 --rules 会默认读引擎所在仓规则，本仓类恒不命中=静默绕过，铁律：每仓 commit-msg 都显式传 --rules）；②规则文件自指逃逸（判据与被判对象同一份 yaml，改文件删段即绕过，防法：路径硬编码进引擎且触发事前对齐层）；③scheme 闸门诚实边界（commit-msg 只要求档案存在、不证时序，同 commit 补档可过，时序靠事后审计兜）。SKILL.md 版本号 v2.4→v2.5。
