# ai-skills

豆包用户的技能集（**公开仓**）。

> **可见性声明（2026-10-21 用户拍板）**：本仓保持 public。文档早期写"私有仓"为建仓时口径，现以本条声明为准。

## 用法

```bash
# 1. 克隆私有仓
git clone https://github.com/kaihu8766-netizen/ai-skills.git
# 2. 安装技能到豆包工作环境
cp -r ai-skills/dual-agent-collab ~/.doubao/agent_mode/workspace/.user_skills/
# 3. 新开一个对话框（刷新技能列表）即可使用
```

## 技能列表

| 技能 | 说明 |
|---|---|
| `dual-agent-collab` | **通用双 Agent 协作模式（v2.7）**：主执行 Agent + DeepSeek 独立评审/讨论 + 人类最终裁决。适用于简历制作、日常工作、日常搜索、写作、方案、产品开发等任意任务。核心：任务路由表（哪些任务必须讨论/复核）、联网取证（关键事实强制搜索验证，来源 S/A/B/C 分级）、轻量档案（无仓库自动存工作区，可溯源）、**降级门禁（第0步：无 key 必须先询问用户再裁决，不可逆类 BLOCKED；降级=degraded 不算独立复核，硬门只认受控通道 RV 档案）**、环境自检（env-check.md）、可选 git 门禁 |

## 使用示例

任何对话框里说一句"**用双 Agent 模式帮我做 X**"（如"用双 Agent 模式帮我做一份前端简历"），主 Agent 会按技能流程：拆解任务 → 与 DeepSeek 讨论方案 → 联网取证执行 → DeepSeek 复核 → 交付并落档案。

> **public 仓安全红线（强制）**：本仓为公开可见，任何提交不得包含——API key / token / 密码 / 真实发票 / 个人真实身份信息 / 内部路径。push 前必须敏感扫描（`grep -rniE "sk-[a-z0-9]{20,}|ghp_[a-z0-9]{20,}|/home/user|ak-[a-z0-9]{20,}"`），key 一律走环境变量（如 `DEEPSEEK_API_KEY`），不得写入任何文件。发现泄露立即 rotate key + 重写历史。
