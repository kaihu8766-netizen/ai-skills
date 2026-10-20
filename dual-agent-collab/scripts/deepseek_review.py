#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""双 Agent 协作：DeepSeek 独立评审调用 + 档案落盘（通用版）。

用途：事前对齐（--phase scheme）与事后复核（--phase review）的统一入口。
行为：调用 DeepSeek API → 响应落盘 <out-dir>/raw/rv-YYYYMMDD-NN-<topic>.json →
      追加索引行到 <out-dir>/索引.md → 打印结论。

项目专用门禁（diff_hash、敏感词通道、gate 规则）不属于本脚本——那是
使用方在 gates.md 描述的 commit-msg 钩子/本地校验层的事。
"""
import argparse, datetime, hashlib, json, os, re, sys, urllib.request, urllib.error

API_URL = "https://api.deepseek.com/chat/completions"
# v2.7（RV-20261021-02 adopted）：统一正式模型名 deepseek-flash（V4.1-Flash-1017，原生多模态视觉）。
# 旧名 deepseek-chat / deepseek-v4-flash 仅靠官方"暂时兼容路由"存活，随时可能断链，禁止回退。
MODEL_DEFAULT = "deepseek-flash"
# 视觉通道护栏（F-C2/RV-20261021-02）：硬截断 ≤3 图/次，防证据稀释；单图 ≤1024 token 计费（输入侧，不计入输出 max_tokens）
MAX_IMAGES = 3
IMG_EXT = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}


def parse_topic(topic: str) -> tuple:
    """topic 形如 RV-20260928-01-XXX → (ymd, nn)。"""
    m = re.match(r"RV-(\d{8})-(\d+)-", topic)
    if not m:
        sys.exit(f"[err] topic 必须形如 RV-YYYYMMDD-NN-主题，收到: {topic}")
    return m.group(1), int(m.group(2))


def build_user_content(prompt: str, images: list) -> object:
    """构造 user 消息：纯文本 → str；带图 → OpenAI 兼容 content 数组（base64 内联）。
    纪律（review-framework 图文双通道）：图不替代原文片段；图须附元数据（URL/视口/时间）于 prompt 文本。
    """
    if not images:
        return prompt
    blocks = [{"type": "text", "text": prompt}]
    for img in images:
        ext = os.path.splitext(img)[1].lower()
        if ext not in IMG_EXT:
            sys.exit(f"[err] 不支持的图片格式: {img}（支持 {sorted(IMG_EXT)}）")
        try:
            raw = open(img, "rb").read()
        except OSError as e:
            sys.exit(f"[err] 无法读取图片: {img}（{e}）")
        if len(raw) > 32 * 1024 * 1024:
            sys.exit(f"[err] 图片超过 32MiB 上限: {img}")
        b64 = __import__("base64").b64encode(raw).decode("utf-8")
        blocks.append({"type": "image_url", "image_url": {"url": f"data:{IMG_EXT[ext]};base64,{b64}"}})
    return blocks


def call_deepseek(api_key: str, prompt: str, max_tokens: int, images: list) -> dict:
    body = json.dumps({
        "model": MODEL_DEFAULT,
        "messages": [
            {"role": "system", "content": "你是独立评审 Agent。评审要严格、具体、可执行，结论必须给出：通过 / 有条件通过（列条件）/ 拒绝（列原因）。不参与执行，避免自我确认偏差。若收到图片：视为辅助交叉印证（非主判据），仍须基于原文片段（路径:行号）作结论；图片元数据见 prompt。"},
            {"role": "user", "content": build_user_content(prompt, images)},
        ],
        "max_tokens": max_tokens,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(API_URL, data=body, method="POST", headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"[err] DeepSeek API HTTP {e.code}: {e.read().decode('utf-8')[:500]}")
    except Exception as e:
        sys.exit(f"[err] DeepSeek API 调用失败: {e}")


def append_index(out_dir: str, row: str) -> None:
    idx = os.path.join(out_dir, "索引.md")
    with open(idx, "a", encoding="utf-8") as f:
        f.write(row)


def main():
    ap = argparse.ArgumentParser(description="DeepSeek 独立评审 + 档案落盘")
    ap.add_argument("--phase", choices=["review", "scheme"], required=True,
                    help="review=事后复核；scheme=事前对齐（方案评审）")
    ap.add_argument("--topic", required=True, help="RV-YYYYMMDD-NN-主题")
    ap.add_argument("--prompt", required=True, help="评审请求内容")
    ap.add_argument("--max-tokens", type=int, default=2500,
                    help="思考链+回答总配额（flash 默认思考模式）。简单评审建议 1500+，带图/复杂评审 2500+；"
                         "若返回空 content 且 usage 显示 reasoning 耗尽，先加配额再排查")
    ap.add_argument("--feature", default=None, help="scheme 通道的方案编号 F-xxx")
    ap.add_argument("--out-dir", default="dual-agent/reviews",
                    help="档案根目录（相对 cwd 或绝对路径），默认 ./dual-agent/reviews")
    ap.add_argument("--force", action="store_true", help="同 topic 已存在时强制重审")
    ap.add_argument("--model", default=MODEL_DEFAULT)
    ap.add_argument("--image", action="append", default=[], metavar="PATH",
                    help="附加图片（可多次，最多 %d 张；JPEG/PNG/GIF/WebP；base64 内联）。"
                         "纪律：图须带元数据（URL/视口/时间）且原文片段仍必贴——图不替代片段；"
                         "图为辅助交叉印证，非主判据" % MAX_IMAGES)
    args = ap.parse_args()

    if len(args.image) > MAX_IMAGES:
        sys.exit(f"[err] --image 最多 {MAX_IMAGES} 张（硬护栏 F-C2），收到 {len(args.image)} 张")

    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        sys.exit("[err] 缺少 DEEPSEEK_API_KEY 环境变量（请勿把 key 写死在脚本/提交里）")

    ymd, nn = parse_topic(args.topic)
    raw_dir = os.path.join(args.out_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    topic_slug = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff-]", "-", args.topic).strip("-")
    fname = f"rv-{ymd}-{nn:02d}-{topic_slug}.json"
    fpath = os.path.join(raw_dir, fname)
    if os.path.exists(fpath) and not args.force:
        print(f"[skip] 已存在: {fpath}（用 --force 重审）")
        return 0

    if args.phase == "scheme" and not args.feature:
        sys.exit("[err] scheme 通道必须提供 --feature F-xxx（方案编号）")

    print(f"[gate] 发起 DeepSeek {args.phase} 评审: {args.topic} （模型={args.model}，图={len(args.image)}）...")
    resp = call_deepseek(api_key, args.prompt, args.max_tokens, args.image)

    content = resp["choices"][0]["message"]["content"]
    usage = resp.get("usage", {})
    # 能力基线锚定（RV-20261021-02 清单外①）：记录"请求名→实际 model 回显→版本"，对抗路由漂移
    requested_model = args.model
    actual_model = resp.get("model", "")
    conclusion = "通过"
    # 匹配顺序：先"有条件通过"再"拒绝"（防"拒绝'无条件通过'表述"等否定句误判），最后"通过"
    for kw in ("有条件通过", "拒绝", "通过"):
        if kw in content[:2000]:
            conclusion = kw
            break

    record = {
        "rv": args.topic,
        "date": ymd,
        "phase": args.phase,
        "feature": args.feature,
        "prompt": args.prompt,
        "response": content,
        "usage": usage,
        "requested_model": requested_model,
        "actual_model": actual_model,
        "images": args.image,
        "conclusion": conclusion,
        # RV-20260929-04 条件：哈希留痕——原始请求/响应 sha256[:16]，防落盘后改写（判据 2 落盘锚点）
        "prompt_hash": hashlib.sha256(args.prompt.encode("utf-8")).hexdigest()[:16],
        "response_hash": hashlib.sha256(content.encode("utf-8")).hexdigest()[:16],
        "created_at": datetime.datetime.now().astimezone().isoformat(),
    }
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

    archname = f"{ymd}-{nn:02d}-{topic_slug}.md"
    row = f"| {nn:02d} | {ymd} | {args.topic} | 见档案（{archname}） | {conclusion} | {archname} | 见档案 | prompt_hash={record['prompt_hash']} |\n"
    append_index(args.out_dir, row)

    print(f"[gate] 评审结论: {conclusion}")
    print(f"[gate] 档案: {fpath}")
    print(f"[gate] 索引: {os.path.join(args.out_dir, '索引.md')}（已追加）")
    if usage:
        print(f"[gate] 用量: in={usage.get('prompt_tokens')} out={usage.get('completion_tokens')} total={usage.get('total_tokens')}")
    print()
    print(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
