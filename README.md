# ai-skills

豆包用户的技能集（私有）。

## 用法

```bash
# 在豆包工作环境安装一个技能
cp -r <skill-name> ~/.doubao/agent_mode/workspace/.user_skills/
```

## 技能列表

| 技能 | 说明 |
|---|---|
| `dual-agent-collab` | 双 Agent 协作评审工作流：主执行 Agent + DeepSeek 独立评审 + 人类最终裁决（事前对齐 / 事后复核 / 评审档案 / 决策记录 / 定期自检） |

> 安全：本仓不含任何 API key（key 一律走环境变量，如 `DEEPSEEK_API_KEY`）。
