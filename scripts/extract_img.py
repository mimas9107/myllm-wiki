#!/usr/bin/env python3
"""
extract_img.py — CMP Wiki 視覺萃取工具
用途：將 PPT/PPTX/PDF 每一頁轉成圖片，再呼叫 Claude Vision API 萃取技術要點
輸出：Markdown 格式，可直接貼入 wiki 或存成 .md 檔

用法：
  python3 scripts/extract_img.py <input_file> [選項]

選項：
  --out <path>        輸出 .md 檔路徑（預設：stdout）
  --pages <n>         只處理前 N 頁（預設：全部）
  --dpi <n>           轉圖解析度（預設：150）
  --prompt <str>      自定義 AI 提示詞
  --keep-images       保留轉換出的 PNG（預設：處理完自動清除）
  --cache-dir <path>  暫存圖片目錄（預設：.cache/extract_img_tmp/）
  --provider <str>    AI 提供者：anthropic | openrouter | gemini（預設：auto）

範例：
  python3 scripts/extract_img.py "Training material/defects/CMP_Defects大觀.ppt" --out .cache/defects_out.md --pages 10
  python3 scripts/extract_img.py "教育訓練/W training.pdf" --out wiki/CMP-Training-W-CMP.md
  python3 scripts/extract_img.py "slides.pptx" --provider openrouter --pages 5
"""

import os
import sys
import argparse
import subprocess
import shutil
import base64
import tempfile
import re
from pathlib import Path
from datetime import datetime


# ─────────────────────────────────────────────
# 預設設定
# ─────────────────────────────────────────────
DEFAULT_CACHE_DIR = "/opt/myllm-wiki/.cache/extract_img_tmp"
DEFAULT_DPI = 150
DEFAULT_MODEL_ANTHROPIC = "claude-sonnet-4-5"
DEFAULT_MODEL_OPENROUTER = "meta-llama/llama-4-scout"  # 免費且支援 vision
DEFAULT_MODEL_GEMINI = "models/gemini-2.0-flash"
DEFAULT_PROMPT = (
    "請仔細閱讀這張投影片或文件頁面，萃取其中的技術知識重點。\n"
    "要求：\n"
    "1. 條列式輸出（繁體中文）\n"
    "2. 保留關鍵英文術語（如 Dishing、Slurry、BTA）\n"
    "3. 若有圖表或顯微照片，描述其呈現的現象或趨勢\n"
    "4. 忽略版面裝飾、公司 logo、頁碼等非技術資訊\n"
    "5. 若此頁為封面或目錄，回傳 [SKIP]\n"
    "輸出格式：直接條列，無需標題"
)


# ─────────────────────────────────────────────
# 步驟 1：轉換輸入檔為 PDF（若非 PDF）
# ─────────────────────────────────────────────
def to_pdf(input_path: Path, work_dir: Path) -> Path:
    suffix = input_path.suffix.lower()
    if suffix == ".pdf":
        return input_path

    print(f"[convert] {input_path.name} → PDF ...", file=sys.stderr)
    result = subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "pdf",
         str(input_path), "--outdir", str(work_dir)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"[error] LibreOffice 轉換失敗：{result.stderr}", file=sys.stderr)
        sys.exit(1)

    pdf_name = input_path.stem + ".pdf"
    pdf_path = work_dir / pdf_name
    if not pdf_path.exists():
        print(f"[error] 找不到轉換後的 PDF：{pdf_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[convert] 完成 → {pdf_path.name}", file=sys.stderr)
    return pdf_path


# ─────────────────────────────────────────────
# 步驟 2：PDF 逐頁轉為 PNG
# ─────────────────────────────────────────────
def pdf_to_pngs(pdf_path: Path, work_dir: Path, dpi: int, max_pages: int = 0) -> list[Path]:
    img_dir = work_dir / "pages"
    img_dir.mkdir(exist_ok=True)

    prefix = str(img_dir / "page")
    cmd = ["pdftoppm", "-r", str(dpi), "-png", str(pdf_path), prefix]
    if max_pages > 0:
        cmd += ["-l", str(max_pages)]

    print(f"[convert] PDF → PNG (dpi={dpi}) ...", file=sys.stderr)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[error] pdftoppm 失敗：{result.stderr}", file=sys.stderr)
        sys.exit(1)

    pngs = sorted(img_dir.glob("page-*.png"), key=lambda p: p.name)
    print(f"[convert] 共 {len(pngs)} 頁", file=sys.stderr)
    return pngs


# ─────────────────────────────────────────────
# 步驟 3：偵測 AI 提供者 + 呼叫視覺 API
# ─────────────────────────────────────────────
def detect_provider() -> str:
    """自動選擇可用的 AI 提供者（Anthropic 需付費訂閱，不納入自動偵測）"""
    if os.environ.get("OPENROUTER_API_KEY_A"):
        return "openrouter"
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini"
    return None


def extract_page_anthropic(client, img_path: Path, prompt: str, page_num: int) -> str:
    with open(img_path, "rb") as f:
        img_data = base64.standard_b64encode(f.read()).decode("utf-8")
    print(f"[vision:anthropic] 第 {page_num} 頁 ...", file=sys.stderr)
    try:
        response = client.messages.create(
            model=DEFAULT_MODEL_ANTHROPIC,
            max_tokens=1500,
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img_data}},
                {"type": "text", "text": prompt}
            ]}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"[ERROR] 第 {page_num} 頁萃取失敗：{e}"


def extract_page_openrouter(img_path: Path, prompt: str, page_num: int) -> str:
    import urllib.request, json
    with open(img_path, "rb") as f:
        img_data = base64.standard_b64encode(f.read()).decode("utf-8")
    print(f"[vision:openrouter] 第 {page_num} 頁 ...", file=sys.stderr)
    api_key = (
        os.environ.get("OPENROUTER_API_KEY_A") or
        os.environ.get("OPENROUTER_API_KEY_B") or
        os.environ.get("OPENROUTER_API_KEY_C")
    )
    payload = json.dumps({
        "model": DEFAULT_MODEL_OPENROUTER,
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_data}"}},
            {"type": "text", "text": prompt}
        ]}]
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://myllm-wiki.local",
            "X-Title": "CMP Wiki Extractor"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[ERROR] 第 {page_num} 頁萃取失敗：{e}"


def extract_page_gemini(img_path: Path, prompt: str, page_num: int) -> str:
    import urllib.request, json
    with open(img_path, "rb") as f:
        img_data = base64.standard_b64encode(f.read()).decode("utf-8")
    print(f"[vision:gemini] 第 {page_num} 頁 ...", file=sys.stderr)
    api_key = os.environ.get("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/{DEFAULT_MODEL_GEMINI}:generateContent?key={api_key}"
    payload = json.dumps({
        "contents": [{"parts": [
            {"inline_data": {"mime_type": "image/png", "data": img_data}},
            {"text": prompt}
        ]}]
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        return f"[ERROR] 第 {page_num} 頁萃取失敗：{e}"


def extract_page(provider: str, client, img_path: Path, prompt: str, page_num: int) -> str:
    if provider == "anthropic":
        return extract_page_anthropic(client, img_path, prompt, page_num)
    elif provider == "openrouter":
        return extract_page_openrouter(img_path, prompt, page_num)
    elif provider == "gemini":
        return extract_page_gemini(img_path, prompt, page_num)
    return "[ERROR] 未知 provider"

# ─────────────────────────────────────────────
# Checkpoint 輔助函數：逐頁即時落地、支援斷點續跑
# ─────────────────────────────────────────────
def checkpoint_dir(work_dir: Path) -> Path:
    d = work_dir / "checkpoints"
    d.mkdir(exist_ok=True)
    return d


def checkpoint_path(ckpt_dir: Path, page_num: int) -> Path:
    return ckpt_dir / f"page_{page_num:04d}.txt"


def load_checkpoint(ckpt_dir: Path, page_num: int):
    """If this page was already extracted, return cached content. Else return None."""
    p = checkpoint_path(ckpt_dir, page_num)
    if p.exists():
        return p.read_text(encoding="utf-8")
    return None


def save_checkpoint(ckpt_dir: Path, page_num: int, content: str):
    """Immediately write this page's content to disk."""
    checkpoint_path(ckpt_dir, page_num).write_text(content, encoding="utf-8")


def build_markdown(input_path: Path, results: list[tuple[int, str]]) -> str:
    title = input_path.stem
    date = datetime.now().strftime("%Y-%m-%d")

    lines = [
        f"# 視覺萃取：{title}",
        f"> 來源：`{input_path}`",
        f"> 萃取日期：{date}",
        f"> 工具：extract_img.py + Claude Vision",
        "",
    ]

    for page_num, content in results:
        if content == "[SKIP]":
            continue
        lines.append(f"## 第 {page_num} 頁")
        lines.append("")
        lines.append(content)
        lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# 主程式
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="PPT/PPTX/PDF 視覺萃取工具，輸出繁中 Markdown"
    )
    parser.add_argument("input", help="輸入檔案路徑")
    parser.add_argument("--out", default=None, help="輸出 .md 路徑（不指定則輸出至 stdout）")
    parser.add_argument("--pages", type=int, default=0, help="只處理前 N 頁（0 = 全部）")
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI, help=f"轉圖解析度（預設 {DEFAULT_DPI}）")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="自定義 AI 提示詞")
    parser.add_argument("--keep-images", action="store_true", help="保留轉換出的 PNG 暫存")
    parser.add_argument("--cache-dir", default=DEFAULT_CACHE_DIR, help="暫存目錄")
    parser.add_argument("--provider", default="auto",
                        choices=["auto", "anthropic", "openrouter", "gemini"],
                        help="AI 視覺提供者（預設 auto 自動偵測）")
    parser.add_argument("--resume", action="store_true",
                        help="斷點續跑：跳過已完成的頁，從中斷處接續萃取")
    args = parser.parse_args()

    # 確認輸入檔存在
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[error] 找不到檔案：{input_path}", file=sys.stderr)
        sys.exit(1)

    # 確認 API Key / 選擇 provider
    provider = args.provider
    client = None
    if provider == "auto":
        provider = detect_provider()
        if not provider:
            print("[error] 找不到任何 API Key（OPENROUTER_API_KEY_A / GEMINI_API_KEY）", file=sys.stderr)
            sys.exit(1)
        print(f"[info] 自動選擇 provider：{provider}", file=sys.stderr)

    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # 建立工作目錄
    work_dir = Path(args.cache_dir) / re.sub(r'[^\w]', '_', input_path.stem)
    work_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 步驟 1: 轉 PDF
        pdf_path = to_pdf(input_path, work_dir)

        # 步驟 2: PDF → PNG
        pngs = pdf_to_pngs(pdf_path, work_dir, args.dpi, args.pages)

        if not pngs:
            print("[error] 未產生任何圖片，請檢查輸入檔案", file=sys.stderr)
            sys.exit(1)

        # 步驟 3: 逐頁視覺萃取（含 checkpoint 機制）
        ckpt_dir = checkpoint_dir(work_dir)
        results = []
        skipped = 0
        for i, png in enumerate(pngs, start=1):
            # --resume: 優先讀取已存在的 checkpoint
            if args.resume:
                cached = load_checkpoint(ckpt_dir, i)
                if cached is not None:
                    results.append((i, cached))
                    skipped += 1
                    print(f"[resume] 第 {i} 頁已有 checkpoint，跳過", file=sys.stderr)
                    continue

            # 呼叫 AI 萃取
            content = extract_page(provider, client, png, args.prompt, i)

            # 立刻寫入 checkpoint（即使後續 quota 耗盡，此頁也已安全落地）
            save_checkpoint(ckpt_dir, i, content)

            results.append((i, content))
            status = '[SKIP]' if content == '[SKIP]' else content[:60].replace('\n', ' ')
            print(f"  [{i}/{len(pngs)}] {status}...", file=sys.stderr)

        if args.resume and skipped > 0:
            print(f"[resume] 共跳過 {skipped} 頁（已有 checkpoint），萃取 {len(pngs) - skipped} 頁", file=sys.stderr)

        # 步驟 4: 組合輸出
        markdown = build_markdown(input_path, results)

        if args.out:
            out_path = Path(args.out)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(markdown, encoding="utf-8")
            print(f"\n[done] 輸出至：{out_path}", file=sys.stderr)
        else:
            print(markdown)

    finally:
        if not args.keep_images:
            shutil.rmtree(work_dir, ignore_errors=True)
            print(f"[cleanup] 已清除暫存：{work_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
