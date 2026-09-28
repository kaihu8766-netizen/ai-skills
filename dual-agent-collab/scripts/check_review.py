#!/usr/bin/env python3
"""通用版评审门禁校验（dual-agent-collab 技能）· RV-20260928-07 落地

闸门：
  1. message 必须含合法 ID 引用（RV-* / GATE-* / DEC-* / ISS-*）
  2. 引用的 RV/GATE 必须在评审索引中存在且状态为 adopted（宽容正则：竖线分隔单元以 adopted 开头）
     - 索引契约：一行一条，UTF-8；状态列 `| adopted |`（允许空格差异，不允许改成 pending/rejected）
  3. 引导期豁免：索引文件不存在/为空 → 放行（打印提示），首个评审档案建立后强制生效
  4. 可选 diff_hash 告警（不阻断）：索引行含 diff_hash 标记时比对当前 staged，不一致仅 warning

用法：check_review.py <message-file>  或  check_review.py --message "<msg>"
环境变量：DUAL_AGENT_REVIEW_DIR 覆盖索引目录（默认 <技能仓>/dual-agent/reviews/）
"""
import os
import re
import sys
from pathlib import Path

DEFAULT_REVIEWS = Path(__file__).resolve().parent.parent / "reviews"

def _index_path() -> Path:
    env = os.environ.get("DUAL_AGENT_REVIEW_DIR", "")
    base = Path(env) if env else DEFAULT_REVIEWS
    return base / "索引.md"

def main() -> int:
    if len(sys.argv) >= 3 and sys.argv[1] == "--message":
        msg = sys.argv[2]
    elif len(sys.argv) == 2 and not sys.argv[1].startswith("--"):
        msg = Path(sys.argv[1]).read_text(encoding="utf-8")
    else:
        msg = Path(sys.argv[1] if len(sys.argv) > 1 else "/dev/stdin").read_text(encoding="utf-8")

    # 闸门 1：合法 ID 引用
    ids = re.findall(r"\b((?:GATE|RV|DEC|ISS)[-:][0-9]{6,8}(?:-[0-9]+)?)\b", msg)
    if not ids:
        print("[check] FAIL：commit message 必须含 ID 引用（GATE-* / RV-* / DEC-* / ISS-*）", file=sys.stderr)
        return 1

    idx = _index_path()
    # 闸门 3：引导期豁免（索引不存在/为空 → 放行）
    if not idx.exists() or not idx.read_text(encoding="utf-8").strip():
        print(f"[check] 引导期豁免：索引不存在（{idx}），跳过 adopted 校验——建立首个评审档案后强制生效", file=sys.stderr)
        return 0

    lines = idx.read_text(encoding="utf-8").splitlines()
    failed = []
    for rid in ids:
        m = re.search(r"(\d{8})-(\d+)$", rid)
        if not m:
            continue
        ymd, no = m.group(1), m.group(2)
        prefix = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}-{int(no):02d}-"
        rv_line = next((ln for ln in lines if prefix in ln), None)
        # 闸门 2：存在 + adopted（宽容空格）
        if rv_line is None:
            failed.append(f"{rid} 未在评审索引中找到（伪造号或档案未入库）")
        elif not re.search(r"\|\s*adopted\b", rv_line):
            failed.append(f"{rid} 在索引中存在但未置 adopted（pending 号不可作为批准依据）")
        else:
            # 闸门 4：可选 diff_hash 告警（不阻断）
            cm = re.search(r"diff_hash[:=]?\s*([0-9a-f]{8,16})", rv_line)
            if cm:
                try:
                    diff = subprocess_sha256()
                    if diff and diff[:16] != cm.group(1):
                        print(f"[check] WARN：{rid} 索引 diff_hash({cm.group(1)}) ≠ 当前 staged({diff})——"
                              f"评审对象与提交对象可能不一致，请复核（不阻断）", file=sys.stderr)
                except Exception:
                    pass
    if failed:
        for f in failed:
            print(f"[check] FAIL：{f}", file=sys.stderr)
        return 1
    print(f"[check] OK：引用 {ids}（存在性 + adopted 校验通过）")
    return 0


def subprocess_sha256() -> str:
    import hashlib
    import subprocess
    r = subprocess.run(["git", "diff", "--cached", "--binary", "--", "."],
                       capture_output=True)
    if not r.stdout.strip():
        return ""
    return hashlib.sha256(r.stdout).hexdigest()[:16]


if __name__ == "__main__":
    sys.exit(main())
