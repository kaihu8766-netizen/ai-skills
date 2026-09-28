#!/bin/sh
# dual-agent-collab 门禁一键安装（RV-20260928-07 落地）
# 用法：scripts/install-gate.sh <项目根目录>
# 效果：在 <项目根>/.githooks/ 安装 commit-msg + git config core.hooksPath .githooks
# 说明：安装本身不需要评审（引导期豁免：索引不存在时提交放行）；
#       安装完成后首次评审档案建立即强制生效。
set -e
ROOT="${1:-$(pwd)}"
SKILL_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
mkdir -p "$ROOT/.githooks"
cp "$SKILL_DIR/scripts/commit-msg" "$ROOT/.githooks/commit-msg"
chmod +x "$ROOT/.githooks/commit-msg"
git -C "$ROOT" config core.hooksPath .githooks
echo "✅ 门禁已安装：$ROOT/.githooks/commit-msg"
echo "   索引目录约定：\$DUAL_AGENT_REVIEW_DIR 或 <技能仓>/reviews/索引.md（引导期豁免，建立首个评审档案后强制）"
